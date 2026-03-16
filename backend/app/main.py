from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, async_session_maker
from app.models.user import User
from app.utils.security import get_password_hash
from app.api import (
    auth_router,
    channels_router,
    posts_router,
    content_types_router,
    queue_router,
    censorship_router,
    products_router,
    settings_router,
    analytics_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await create_admin_user()
    yield


async def create_admin_user():
    async with async_session_maker() as db:
        from sqlalchemy import select

        result = await db.execute(select(User).where(User.username == settings.ADMIN_USERNAME))
        if not result.scalar_one_or_none():
            admin = User(
                username=settings.ADMIN_USERNAME,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                is_active=True,
            )
            db.add(admin)
            await db.commit()


app = FastAPI(
    title="Autoposting Platform",
    description="Multi-channel content management and auto-posting system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(channels_router)
app.include_router(posts_router)
app.include_router(content_types_router)
app.include_router(queue_router)
app.include_router(censorship_router)
app.include_router(products_router)
app.include_router(settings_router)
app.include_router(analytics_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
