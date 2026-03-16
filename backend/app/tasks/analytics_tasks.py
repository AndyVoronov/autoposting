import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, and_

from app.tasks.celery_app import celery_app
from app.database import async_session_maker
from app.models.post import Post, PublishLog
from app.models.channel import Channel
from app.models.analytics import Analytics


@celery_app.task(bind=True)
def collect_analytics(self):
    return asyncio.run(_collect_analytics())


async def _collect_analytics():
    async with async_session_maker() as db:
        result = await db.execute(
            select(PublishLog)
            .where(PublishLog.status == "published")
            .order_by(PublishLog.published_at.desc())
            .limit(50)
        )
        recent_logs = result.scalars().all()

        collected = 0
        for log in recent_logs:
            existing = await db.execute(
                select(Analytics).where(
                    and_(
                        Analytics.post_id == log.post_id,
                        Analytics.platform == log.platform,
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            post_result = await db.execute(select(Post).where(Post.id == log.post_id))
            post = post_result.scalar_one_or_none()
            if not post:
                continue

            channel_result = await db.execute(select(Channel).where(Channel.id == post.channel_id))
            channel = channel_result.scalar_one_or_none()
            if not channel:
                continue

            analytics_data = await fetch_analytics_from_platform(
                platform=log.platform,
                channel=channel,
                message_id=log.message_id,
            )

            if analytics_data:
                analytics = Analytics(
                    post_id=post.id,
                    platform=log.platform,
                    views=analytics_data.get("views", 0),
                    likes=analytics_data.get("likes", 0),
                    shares=analytics_data.get("shares", 0),
                    comments=analytics_data.get("comments", 0),
                    clicks=0,
                )
                db.add(analytics)
                collected += 1

        await db.commit()
        return {"collected": collected}


async def fetch_analytics_from_platform(
    platform: str, channel: Channel, message_id: str | None
) -> dict | None:
    if not message_id:
        return None

    try:
        if platform == "telegram":
            return await fetch_telegram_stats(channel, message_id)
        elif platform == "vk":
            return await fetch_vk_stats(channel, message_id)
        elif platform == "wordpress":
            return await fetch_wordpress_stats(channel, message_id)
    except Exception as e:
        print(f"Error fetching analytics for {platform}: {e}")
        return None

    return None


async def fetch_telegram_stats(channel: Channel, message_id: str) -> dict:
    import httpx
    from app.config import settings

    if not settings.TELEGRAM_BOT_TOKEN:
        return {"views": 0, "likes": 0, "shares": 0, "comments": 0}

    config = channel.config or {}
    chat_id = config.get("chat_id") or config.get("channel_id")

    if not chat_id:
        return {"views": 0, "likes": 0, "shares": 0, "comments": 0}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMessage",
                params={"chat_id": chat_id, "message_id": message_id},
            )
            data = response.json()
            if data.get("ok"):
                msg = data.get("result", {})
                views = msg.get("views", 0)
                return {"views": views, "likes": 0, "shares": 0, "comments": 0}
        except Exception:
            pass

    return {"views": 0, "likes": 0, "shares": 0, "comments": 0}


async def fetch_vk_stats(channel: Channel, message_id: str) -> dict:
    import httpx
    from app.config import settings

    if not settings.VK_ACCESS_TOKEN or not settings.VK_GROUP_ID:
        return {"views": 0, "likes": 0, "shares": 0, "comments": 0}

    try:
        post_id = int(message_id)
    except ValueError:
        return {"views": 0, "likes": 0, "shares": 0, "comments": 0}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                "https://api.vk.com/method/stats.getPostReach",
                params={
                    "access_token": settings.VK_ACCESS_TOKEN,
                    "owner_id": -settings.VK_GROUP_ID,
                    "post_id": post_id,
                    "v": "5.131",
                },
            )
            data = response.json()
            if "response" in data:
                stats = data["response"]
                return {
                    "views": stats.get("reach", 0),
                    "likes": stats.get("likes", 0),
                    "shares": stats.get("shares", 0),
                    "comments": stats.get("comments", 0),
                }
        except Exception:
            pass

    return {"views": 0, "likes": 0, "shares": 0, "comments": 0}


async def fetch_wordpress_stats(channel: Channel, message_id: str) -> dict:
    return {"views": 0, "likes": 0, "shares": 0, "comments": 0}
