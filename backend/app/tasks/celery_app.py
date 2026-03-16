from celery import Celery
from celery.schedules import crontab

from app.config import settings
from app.database import async_session_maker
from app.models.post import Post, PostStatus, PublishLog
from app.models.channel import Channel, ChannelContent
from app.models.censorship import CensorshipRule
from app.models.analytics import Analytics

from app.services.publishers import telegram_publisher, vk_publisher, wordpress_publisher
from app.services.ai import ai_service
from app.services.censorship import CensorshipService
from app.services.content import (
    reddit_source,
    horoscope_source,
    animal_facts_source,
    news_source,
    city_source,
    affiliate_source,
)
from app.services.media import unsplash_service

celery_app = Celery(
    "autoposting",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.content_tasks",
        "app.tasks.publish_tasks",
        "app.tasks.cleanup_tasks",
        "app.tasks.analytics_tasks",
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
    "generate-city-content": {
        "task": "app.tasks.content_tasks.generate_city_content",
        "schedule": crontab(hour="7,13,19", minute=0),
    },
    "generate-affiliate-posts": {
        "task": "app.tasks.content_tasks.generate_affiliate_posts",
        "schedule": crontab(hour="10,16,22", minute=0),
    },
    "process-publish-queue": {
        "task": "app.tasks.publish_tasks.process_publish_queue",
        "schedule": crontab(minute="*"),
    },
    "collect-analytics-every-30-minutes": {
        "task": "app.tasks.analytics_tasks.collect_analytics",
        "schedule": crontab(minute="*/30"),
    },
    "cleanup-old-posts": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_posts",
        "schedule": crontab(hour=3, minute=0),
    },
}
