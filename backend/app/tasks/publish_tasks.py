from datetime import datetime
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.post import Post, PublishQueue, PublishLog, PostStatus
from app.models.channel import Channel, Platform
from app.services.publishers import telegram_publisher, vk_publisher, wordpress_publisher

sync_engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
SyncSession = sessionmaker(bind=sync_engine)


@shared_task(name="app.tasks.publish_tasks.process_publish_queue")
def process_publish_queue():
    import asyncio

    db = SyncSession()
    try:
        queue_items = (
            db.query(PublishQueue)
            .filter(
                PublishQueue.status == "pending",
                PublishQueue.scheduled_at <= datetime.utcnow(),
                PublishQueue.attempts < PublishQueue.max_attempts,
            )
            .limit(10)
            .all()
        )

        results = []
        for item in queue_items:
            post = db.query(Post).filter(Post.id == item.post_id).first()
            if not post:
                item.status = "failed"
                item.error_message = "Post not found"
                continue

            channel = db.query(Channel).filter(Channel.id == post.channel_id).first()
            if not channel:
                item.status = "failed"
                item.error_message = "Channel not found"
                continue

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(publish_to_platform(item.platform, channel, post))
                loop.close()
            except Exception as e:
                loop.close()
                result = {"success": False, "error": str(e)}

            if result.get("success"):
                item.status = "published"
                post.status = PostStatus.PUBLISHED
                post.published_at = datetime.utcnow()

                log = PublishLog(
                    post_id=post.id,
                    platform=item.platform,
                    status="success",
                    message_id=str(result.get("message_id", "")),
                )
                db.add(log)
                results.append({"post_id": post.id, "status": "published"})
            else:
                item.attempts += 1
                item.error_message = result.get("error", "Unknown error")

                if item.attempts >= item.max_attempts:
                    item.status = "failed"
                    post.status = PostStatus.FAILED

                    log = PublishLog(
                        post_id=post.id,
                        platform=item.platform,
                        status="failed",
                        error_message=item.error_message,
                    )
                    db.add(log)

                results.append(
                    {"post_id": post.id, "status": "failed", "error": item.error_message}
                )

        db.commit()
        return {"processed": len(results), "results": results}
    finally:
        db.close()


async def publish_to_platform(platform: Platform, channel: Channel, post: Post) -> dict:
    chat_id = channel.config.get("chat_id") if channel.config else None

    if not chat_id:
        return {"success": False, "error": "No chat_id in channel config"}

    if platform == Platform.TELEGRAM:
        return await publish_to_telegram(chat_id, post)
    elif platform == Platform.VK:
        return await publish_to_vk(chat_id, post)
    elif platform == Platform.WORDPRESS:
        return await publish_to_wordpress(post)
    else:
        return {"success": False, "error": f"Unknown platform: {platform}"}


async def publish_to_telegram(chat_id: str, post: Post) -> dict:
    text = telegram_publisher.format_post(post.title, post.body, post.source_url)

    if post.media_urls and len(post.media_urls) > 0:
        result = await telegram_publisher.send_photo(
            chat_id=chat_id,
            photo_url=post.media_urls[0],
            caption=text[:1024],
        )
    else:
        result = await telegram_publisher.send_message(
            chat_id=chat_id,
            text=text,
        )

    if result.get("ok"):
        return {
            "success": True,
            "message_id": result.get("result", {}).get("message_id"),
        }
    else:
        return {"success": False, "error": result.get("error", "Unknown error")}


async def publish_to_vk(group_id: str, post: Post) -> dict:
    text = vk_publisher.format_post(post.title, post.body, post.source_url)

    result = await vk_publisher.wall_post(message=text)

    if result.get("success"):
        return {"success": True, "message_id": result.get("post_id")}
    else:
        return {"success": False, "error": result.get("error", "Unknown error")}


async def publish_to_wordpress(post: Post) -> dict:
    content = wordpress_publisher.format_content(
        post.title or "Без заголовка",
        post.body,
        post.source_url,
    )

    result = await wordpress_publisher.create_post(
        title=post.title or "Без заголовка",
        content=content,
        status="publish",
    )

    if result.get("success"):
        return {"success": True, "message_id": result.get("post_id")}
    else:
        return {"success": False, "error": result.get("error", "Unknown error")}


@shared_task(name="app.tasks.publish_tasks.schedule_post")
def schedule_post(post_id: int, platform: str, scheduled_at: str):
    db = SyncSession()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return {"error": "Post not found"}

        scheduled_dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))

        queue_item = PublishQueue(
            post_id=post_id,
            platform=platform,
            scheduled_at=scheduled_dt,
        )
        db.add(queue_item)

        post.status = PostStatus.SCHEDULED
        post.scheduled_at = scheduled_dt

        db.commit()
        return {"success": True, "queue_id": queue_item.id}
    finally:
        db.close()
