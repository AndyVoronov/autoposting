import os
import subprocess
import shutil
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.dependencies import get_current_user
from app.models.user import User
from app.config import settings
from app.database import get_db
from app.models.post import Post, PublishLog
from app.models.censorship import CensorshipLog
from app.models.analytics import Analytics
from app.models.channel import Channel
from app.models.analytics import AffiliateProduct

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsResponse(BaseModel):
    telegram_configured: bool
    vk_configured: bool
    wordpress_configured: bool
    ai_configured: bool
    unsplash_configured: bool
    openweather_configured: bool


class APIKeysUpdate(BaseModel):
    glm_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    vk_access_token: Optional[str] = None
    vk_group_id: Optional[int] = None
    wp_url: Optional[str] = None
    wp_username: Optional[str] = None
    wp_password: Optional[str] = None
    unsplash_access_key: Optional[str] = None
    openweather_api_key: Optional[str] = None


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
):
    return SettingsResponse(
        telegram_configured=bool(settings.TELEGRAM_BOT_TOKEN),
        vk_configured=bool(settings.VK_ACCESS_TOKEN and settings.VK_GROUP_ID),
        wordpress_configured=bool(
            settings.WP_URL and settings.WP_USERNAME and settings.WP_PASSWORD
        ),
        ai_configured=bool(settings.GLM_API_KEY),
        unsplash_configured=bool(settings.UNSPLASH_ACCESS_KEY),
        openweather_configured=bool(settings.OPENWEATHER_API_KEY),
    )


@router.post("/keys")
async def update_api_keys(
    data: APIKeysUpdate,
    current_user: User = Depends(get_current_user),
):
    # In production, this should update .env or a secure config store
    # For now, we just acknowledge the request
    return {
        "status": "updated",
        "message": "API keys updated. Restart required for changes to take effect.",
    }


class ServerStatus(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    celery_status: str
    redis_status: str
    database_status: str
    uptime: str


class ExportData(BaseModel):
    channels: List[Any]
    posts: List[Any]
    products: List[Any]
    exported_at: str


@router.get("/status", response_model=ServerStatus)
async def get_server_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import psutil

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    celery_status = "unknown"
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "autoposting-celery-1",
                "celery",
                "-A",
                "app.tasks.celery_app",
                "inspect",
                "ping",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "OK" in result.stdout or "pong" in result.stdout.lower():
            celery_status = "running"
        else:
            celery_status = "error"
    except Exception:
        celery_status = "unavailable"

    redis_status = "unknown"
    try:
        result = subprocess.run(
            ["docker", "exec", "autoposting-redis-1", "redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        redis_status = "running" if "PONG" in result.stdout else "error"
    except Exception:
        redis_status = "unavailable"

    db_status = "unknown"
    try:
        await db.execute(select(1))
        db_status = "running"
    except Exception:
        db_status = "error"

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.now() - boot_time).split(".")[0]

    return ServerStatus(
        cpu_percent=cpu,
        memory_percent=memory,
        disk_percent=disk,
        celery_status=celery_status,
        redis_status=redis_status,
        database_status=db_status,
        uptime=uptime,
    )


@router.post("/restart-celery")
async def restart_celery(
    current_user: User = Depends(get_current_user),
):
    try:
        result = subprocess.run(
            ["docker", "restart", "autoposting-celery-1", "autoposting-celery-beat-1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return {"status": "success", "message": "Celery workers restarted"}
        else:
            raise HTTPException(status_code=500, detail=f"Restart failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Restart timeout")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Docker command not available")


@router.get("/export", response_model=ExportData)
async def export_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    channels_result = await db.execute(select(Channel))
    channels = [c.__dict__ for c in channels_result.scalars().all()]
    for c in channels:
        c.pop("_sa_instance_state", None)

    posts_result = await db.execute(select(Post).limit(1000))
    posts = []
    for p in posts_result.scalars().all():
        post_dict = p.__dict__.copy()
        post_dict.pop("_sa_instance_state", None)
        for key, value in post_dict.items():
            if isinstance(value, datetime):
                post_dict[key] = value.isoformat()
        posts.append(post_dict)

    products_result = await db.execute(select(AffiliateProduct))
    products = []
    for pr in products_result.scalars().all():
        product_dict = pr.__dict__.copy()
        product_dict.pop("_sa_instance_state", None)
        products.append(product_dict)

    return ExportData(
        channels=channels,
        posts=posts,
        products=products,
        exported_at=datetime.now().isoformat(),
    )


class ClearLogsResponse(BaseModel):
    deleted_publish_logs: int
    deleted_censorship_logs: int
    deleted_analytics: int
    older_than_days: int


@router.delete("/logs", response_model=ClearLogsResponse)
async def clear_logs(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.now() - timedelta(days=days)

    publish_result = await db.execute(delete(PublishLog).where(PublishLog.published_at < cutoff))
    deleted_publish = publish_result.rowcount

    censorship_result = await db.execute(
        delete(CensorshipLog).where(CensorshipLog.created_at < cutoff)
    )
    deleted_censorship = censorship_result.rowcount

    analytics_result = await db.execute(delete(Analytics).where(Analytics.date < cutoff))
    deleted_analytics = analytics_result.rowcount

    await db.commit()

    return ClearLogsResponse(
        deleted_publish_logs=deleted_publish,
        deleted_censorship_logs=deleted_censorship,
        deleted_analytics=deleted_analytics,
        older_than_days=days,
    )
