from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "autoposting",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.content_tasks",
        "app.tasks.publish_tasks",
        "app.tasks.cleanup_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

celery_app.conf.beat_schedule = {
    "fetch-reddit-every-30-minutes": {
        "task": "app.tasks.content_tasks.fetch_reddit_content",
        "schedule": crontab(minute="*/30"),
    },
    "generate-horoscopes-daily": {
        "task": "app.tasks.content_tasks.generate_horoscopes",
        "schedule": crontab(hour=0, minute=5),
    },
    "generate-animal-facts": {
        "task": "app.tasks.content_tasks.generate_animal_facts",
        "schedule": crontab(hour="8,14,20", minute=0),
    },
    "fetch-news-every-15-minutes": {
        "task": "app.tasks.content_tasks.fetch_news_content",
        "schedule": crontab(minute="*/15"),
    },
    "process-publish-queue": {
        "task": "app.tasks.publish_tasks.process_publish_queue",
        "schedule": crontab(minute="*"),
    },
    "cleanup-old-posts": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_posts",
        "schedule": crontab(hour=3, minute=0),
    },
}
