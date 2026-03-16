from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.post import Post, PostStatus, PublishLog
from app.models.analytics import Analytics, AffiliateClick

router = APIRouter(prefix="/analytics", tags=["analytics"])


class DashboardStats(BaseModel):
    total_channels: int
    total_posts: int
    pending_posts: int
    published_today: int
    total_views: int
    total_clicks: int


class PostStats(BaseModel):
    post_id: int
    title: Optional[str]
    views: int
    likes: int
    shares: int
    comments: int
    clicks: int
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class DailyStats(BaseModel):
    date: str
    posts: int
    views: int
    clicks: int


class TopPost(BaseModel):
    id: int
    title: Optional[str]
    views: int
    platform: str
    channel_name: Optional[str] = None


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.channel import Channel

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    total_channels = await db.scalar(select(func.count(Channel.id)))
    total_posts = await db.scalar(select(func.count(Post.id)))
    pending_posts = await db.scalar(
        select(func.count(Post.id)).where(
            Post.status.in_([PostStatus.PENDING, PostStatus.SCHEDULED])
        )
    )
    published_today = await db.scalar(
        select(func.count(Post.id)).where(
            Post.status == PostStatus.PUBLISHED,
            Post.published_at >= today,
        )
    )
    total_views = await db.scalar(select(func.sum(Analytics.views))) or 0
    total_clicks = await db.scalar(select(func.sum(Analytics.clicks))) or 0

    return DashboardStats(
        total_channels=total_channels or 0,
        total_posts=total_posts or 0,
        pending_posts=pending_posts or 0,
        published_today=published_today or 0,
        total_views=total_views or 0,
        total_clicks=total_clicks or 0,
    )


@router.get("/posts/{post_id}", response_model=PostStats)
async def get_post_stats(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Analytics).where(Analytics.post_id == post_id))
    analytics = result.scalar_one_or_none()

    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()

    if not post:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Post not found")

    return PostStats(
        post_id=post_id,
        title=post.title,
        views=analytics.views if analytics else 0,
        likes=analytics.likes if analytics else 0,
        shares=analytics.shares if analytics else 0,
        comments=analytics.comments if analytics else 0,
        clicks=analytics.clicks if analytics else 0,
        published_at=post.published_at,
    )


@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = []

    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - 1 - i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        posts_count = await db.scalar(
            select(func.count(Post.id)).where(
                Post.status == PostStatus.PUBLISHED,
                Post.published_at >= day_start,
                Post.published_at < day_end,
            )
        )

        views = await db.scalar(
            select(func.sum(Analytics.views)).where(
                Analytics.date >= day_start,
                Analytics.date < day_end,
            )
        )

        clicks = await db.scalar(
            select(func.sum(Analytics.clicks)).where(
                Analytics.date >= day_start,
                Analytics.date < day_end,
            )
        )

        result.append(
            DailyStats(
                date=day_start.strftime("%Y-%m-%d"),
                posts=posts_count or 0,
                views=views or 0,
                clicks=clicks or 0,
            )
        )

    return result


@router.get("/top-posts", response_model=List[TopPost])
async def get_top_posts(
    limit: int = 10,
    period_days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.channel import Channel

    period_start = datetime.utcnow() - timedelta(days=period_days)

    result = await db.execute(
        select(Analytics, Post, Channel)
        .join(Post, Analytics.post_id == Post.id)
        .join(Channel, Post.channel_id == Channel.id)
        .where(Analytics.date >= period_start)
        .order_by(desc(Analytics.views))
        .limit(limit)
    )

    posts = []
    for analytics, post, channel in result.all():
        posts.append(
            TopPost(
                id=post.id,
                title=post.title,
                views=analytics.views,
                platform=analytics.platform,
                channel_name=channel.name,
            )
        )

    return posts


@router.get("/referral-clicks")
async def get_referral_clicks(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.analytics import AffiliateProduct

    period_start = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(AffiliateClick, AffiliateProduct)
        .join(AffiliateProduct, AffiliateClick.product_id == AffiliateProduct.id)
        .where(AffiliateClick.clicked_at >= period_start)
        .order_by(desc(AffiliateClick.clicked_at))
        .limit(100)
    )

    clicks = []
    for click, product in result.all():
        clicks.append(
            {
                "id": click.id,
                "product_name": product.name,
                "product_category": product.category,
                "post_id": click.post_id,
                "channel_id": click.channel_id,
                "clicked_at": click.clicked_at.isoformat(),
            }
        )

    return clicks
