# API endpoints
from app.api.auth import router as auth_router
from app.api.channels import router as channels_router
from app.api.posts import router as posts_router
from app.api.content_types import router as content_types_router
from app.api.queue import router as queue_router
from app.api.censorship import router as censorship_router
from app.api.products import router as products_router
from app.api.settings import router as settings_router
from app.api.analytics import router as analytics_router

__all__ = [
    "auth_router",
    "channels_router",
    "posts_router",
    "content_types_router",
    "queue_router",
    "censorship_router",
    "products_router",
    "settings_router",
    "analytics_router",
]
