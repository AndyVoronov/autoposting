"""
Seed script to populate initial data.
Run: python -m app.seed
"""

import asyncio
from sqlalchemy import select
from app.database import async_session_maker
from app.models.channel import ContentTypeModel, ContentType
from app.models.user import User
from app.utils.security import get_password_hash


async def seed_content_types():
    """Create initial content types"""
    async with async_session_maker() as db:
        # Check if already seeded
        result = await db.execute(select(ContentTypeModel))
        if result.scalars().first():
            print("Content types already exist, skipping seed")
            return

        content_types_data = [
            {
                "name": "Интересные факты о Москве",
                "type": ContentType.MOSCOW_FACTS,
                "description": "Исторические факты, архитектура, неизвестные места Москвы",
                "config": {
                    "fact_types": ["history", "architecture", "unknown"],
                    "use_ai": True,
                },
                "is_active": True,
            },
            {
                "name": "Новости Москвы",
                "type": ContentType.NEWS,
                "description": "Новости из московских источников с AI-фильтрацией",
                "config": {
                    "sources": ["mos_ru", "moscow_live", "tass", "ria", "rbc"],
                    "summarize": True,
                    "filter_interesting": True,
                },
                "is_active": True,
            },
            {
                "name": "Городской контент",
                "type": ContentType.CITY,
                "description": "Погода и городские события",
                "config": {
                    "cities": ["moscow"],
                    "include_weather": True,
                    "include_greeting": True,
                },
                "is_active": True,
            },
            {
                "name": "Reddit контент",
                "type": ContentType.REDDIT,
                "description": "Контент с Reddit",
                "config": {
                    "subreddits": ["interestingasfuck", "todayilearned"],
                    "min_score": 1000,
                    "translate": True,
                    "rewrite": True,
                },
                "is_active": False,
            },
            {
                "name": "Гороскопы",
                "type": ContentType.HOROSCOPE,
                "description": "Ежедневные гороскопы",
                "config": {
                    "use_ai": True,
                },
                "is_active": False,
            },
            {
                "name": "Факты о животных",
                "type": ContentType.ANIMAL_FACTS,
                "description": "Интересные факты о животных",
                "config": {
                    "use_ai": True,
                },
                "is_active": False,
            },
        ]

        for data in content_types_data:
            content_type = ContentTypeModel(**data)
            db.add(content_type)

        await db.commit()
        print(f"Created {len(content_types_data)} content types")


async def seed_admin_user():
    """Create admin user if not exists"""
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists, skipping")
            return

        admin = User(
            username="admin",
            hashed_password=get_password_hash("Ch4ng3Th1sP4ssw0rd!"),
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        print("Created admin user (username: admin)")


async def main():
    print("Seeding database...")
    await seed_content_types()
    await seed_admin_user()
    print("Seed completed!")


if __name__ == "__main__":
    asyncio.run(main())
