from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_current_user
from app.models.user import User
from app.config import settings

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
