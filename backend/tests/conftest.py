import asyncio
import pytest
import pytest_asyncio
import respx
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.channel import Channel, ContentTypeModel, ChannelContent, Platform, ContentType
from app.models.post import Post, PostStatus, PublishQueue
from app.models.censorship import CensorshipRule
from app.models.analytics import AffiliateProduct, Analytics
from app.utils.security import get_password_hash


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as db:
        admin = User(
            username="testadmin",
            password_hash=get_password_hash("testpass123"),
            is_active=True,
        )
        db.add(admin)
        await db.commit()

        yield db

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def auth_header(client):
    response = await client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_channel(db):
    channel = Channel(
        name="Test Channel",
        slug="test-channel",
        platform=Platform.TELEGRAM,
        config={"chat_id": "@testchannel"},
        is_active=True,
    )
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel


@pytest_asyncio.fixture
async def sample_content_type(db):
    content_type = ContentTypeModel(
        name="Reddit Content",
        type=ContentType.REDDIT,
        description="Content from Reddit",
        is_active=True,
    )
    db.add(content_type)
    await db.commit()
    await db.refresh(content_type)
    return content_type


@pytest_asyncio.fixture
async def sample_post(db, sample_channel):
    post = Post(
        channel_id=sample_channel.id,
        title="Test Post",
        body="This is a test post content",
        status=PostStatus.DRAFT,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@pytest_asyncio.fixture
async def sample_product(db):
    product = AffiliateProduct(
        name="Test Product",
        category="electronics",
        ref_url="https://example.com/product/123",
        description="A test product for testing",
        is_active=True,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@pytest_asyncio.fixture
async def sample_censorship_rule(db):
    rule = CensorshipRule(
        pattern="forbidden_word",
        pattern_type="word",
        rule_type="banned",
        category="test",
        is_active=True,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@pytest_asyncio.fixture
async def sample_queue_item(db, sample_post):
    queue_item = PublishQueue(
        post_id=sample_post.id,
        platform=Platform.TELEGRAM,
        scheduled_at=datetime.utcnow(),
        status="pending",
    )
    db.add(queue_item)
    await db.commit()
    await db.refresh(queue_item)
    return queue_item


@pytest.fixture
def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_ai_service():
    with patch("app.services.ai.glm.ai_service") as mock:
        mock.chat = AsyncMock(return_value="AI generated response")
        mock.translate_to_russian = AsyncMock(return_value="Переведенный текст")
        mock.rewrite_text = AsyncMock(return_value="Переписанный текст")
        mock.generate_horoscope = AsyncMock(return_value="Гороскоп на сегодня")
        mock.generate_animal_fact = AsyncMock(return_value="Интересный факт")
        mock.summarize_news = AsyncMock(return_value="Краткая новость")
        mock.improve_text = AsyncMock(return_value="Улучшенный текст")
        mock.shorten_text = AsyncMock(return_value="Сокращенный текст")
        mock.rewrite_text_for_post = AsyncMock(return_value="Переписанный текст")
        mock.check_censorship = AsyncMock(
            return_value={"safe": True, "reasons": [], "suggestion": None}
        )
        yield mock


@pytest.fixture
def mock_telegram_api():
    with respx.mock(base_url="https://api.telegram.org") as mock:
        mock.post("/bot123456:ABC/sendMessage").mock(
            return_value=respx.Response(200, json={"ok": True, "result": {"message_id": 123}})
        )
        mock.post("/bot123456:ABC/sendPhoto").mock(
            return_value=respx.Response(200, json={"ok": True, "result": {"message_id": 124}})
        )
        mock.post("/bot123456:ABC/getMe").mock(
            return_value=respx.Response(200, json={"ok": True, "result": {"id": 123456}})
        )
        mock.post("/bot123456:ABC/getChat").mock(
            return_value=respx.Response(200, json={"ok": True, "result": {"id": -1001234567890}})
        )
        yield mock


@pytest.fixture
def mock_vk_api():
    with respx.mock(base_url="https://api.vk.com/method") as mock:
        mock.post("/wall.post").mock(
            return_value=respx.Response(200, json={"response": {"post_id": 123}})
        )
        mock.get("/photos.getWallUploadServer").mock(
            return_value=respx.Response(
                200, json={"response": {"upload_url": "https://vk.com/upload"}}
            )
        )
        mock.get("/groups.getById").mock(
            return_value=respx.Response(
                200, json={"response": [{"id": 123456, "name": "Test Group"}]}
            )
        )
        yield mock


@pytest.fixture
def mock_wordpress_api():
    with respx.mock(base_url="https://example.com/wp-json/wp/v2") as mock:
        mock.post("/posts").mock(
            return_value=respx.Response(
                201, json={"id": 123, "link": "https://example.com/post/123"}
            )
        )
        mock.get("/categories").mock(
            return_value=respx.Response(200, json=[{"id": 1, "name": "Uncategorized"}])
        )
        mock.post("/media").mock(
            return_value=respx.Response(
                201, json={"id": 456, "source_url": "https://example.com/image.jpg"}
            )
        )
        yield mock


@pytest.fixture
def mock_reddit_api():
    with respx.mock(base_url="https://www.reddit.com") as mock:
        mock.get("/r/interestingasfuck/hot.json").mock(
            return_value=respx.Response(
                200,
                json={
                    "data": {
                        "children": [
                            {
                                "data": {
                                    "id": "abc123",
                                    "title": "Amazing fact!",
                                    "selftext": "This is the post body",
                                    "url": "https://www.reddit.com/r/interestingasfuck/comments/abc123",
                                    "score": 5000,
                                    "num_comments": 200,
                                    "subreddit": "interestingasfuck",
                                    "author": "testuser",
                                    "created_utc": 1700000000,
                                    "over_18": False,
                                    "is_video": False,
                                    "url": "https://i.redd.it/test.jpg",
                                }
                            }
                        ]
                    }
                },
            )
        )
        yield mock


@pytest.fixture
def mock_news_rss():
    rss_content = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test News</title>
            <item>
                <title>Breaking News</title>
                <description>Important news content</description>
                <link>https://example.com/news/1</link>
                <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>"""
    with respx.mock() as mock:
        mock.get("https://tass.ru/rss/v2.xml").mock(
            return_value=respx.Response(200, text=rss_content)
        )
        yield mock


@pytest.fixture
def mock_unsplash_api():
    with respx.mock(base_url="https://api.unsplash.com") as mock:
        mock.get("/search/photos").mock(
            return_value=respx.Response(
                200,
                json={
                    "results": [
                        {
                            "id": "abc123",
                            "urls": {"regular": "https://images.unsplash.com/photo.jpg"},
                            "alt_description": "Test image",
                            "user": {"name": "Test User"},
                        }
                    ]
                },
            )
        )
        mock.get("/photos/random").mock(
            return_value=respx.Response(
                200,
                json={
                    "id": "xyz789",
                    "urls": {"regular": "https://images.unsplash.com/random.jpg"},
                    "alt_description": "Random image",
                    "user": {"name": "Random User"},
                },
            )
        )
        yield mock


@pytest.fixture
def mock_weather_api():
    with respx.mock(base_url="https://api.openweathermap.org") as mock:
        mock.get("/data/2.5/weather").mock(
            return_value=respx.Response(
                200,
                json={
                    "main": {"temp": 20, "humidity": 65},
                    "weather": [{"description": "clear sky"}],
                    "name": "Moscow",
                },
            )
        )
        yield mock


@pytest.fixture
def mock_glm_api():
    with respx.mock(base_url="https://api.z.ai/v1") as mock:
        mock.post("/chat/completions").mock(
            return_value=respx.Response(
                200, json={"choices": [{"message": {"content": "AI generated response"}}]}
            )
        )
        yield mock
