from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.post import Post, PublishLog, PublishQueue
from app.models.censorship import CensorshipLog
from app.models.analytics import AffiliateClick

sync_engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
SyncSession = sessionmaker(bind=sync_engine)


@shared_task(name="app.tasks.cleanup_tasks.cleanup_old_posts")
def cleanup_old_posts(days_old: int = 30):
    db = SyncSession()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days_old)

        deleted_posts = (
            db.query(Post)
            .filter(
                Post.status.in_(["published", "rejected", "failed"]),
                Post.created_at < cutoff,
            )
            .delete()
        )

        deleted_logs = db.query(PublishLog).filter(PublishLog.published_at < cutoff).delete()

        deleted_queue = (
            db.query(PublishQueue)
            .filter(
                PublishQueue.status.in_(["published", "failed"]),
                PublishQueue.created_at < cutoff,
            )
            .delete()
        )

        deleted_censorship = (
            db.query(CensorshipLog).filter(CensorshipLog.created_at < cutoff).delete()
        )

        deleted_clicks = (
            db.query(AffiliateClick).filter(AffiliateClick.clicked_at < cutoff).delete()
        )

        db.commit()

        return {
            "deleted_posts": deleted_posts,
            "deleted_logs": deleted_logs,
            "deleted_queue": deleted_queue,
            "deleted_censorship": deleted_censorship,
            "deleted_clicks": deleted_clicks,
        }
    finally:
        db.close()


@shared_task(name="app.tasks.cleanup_tasks.cleanup_failed_queue")
def cleanup_failed_queue(hours_old: int = 24):
    db = SyncSession()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours_old)

        deleted = (
            db.query(PublishQueue)
            .filter(
                PublishQueue.status == "failed",
                PublishQueue.created_at < cutoff,
            )
            .delete()
        )

        db.commit()
        return {"deleted": deleted}
    finally:
        db.close()
