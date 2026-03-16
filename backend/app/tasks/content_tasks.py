from datetime import datetime
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.services.content import (
    reddit_source,
    horoscope_source,
    animal_facts_source,
    news_source,
    city_source,
    moscow_facts_source,
    affiliate_source,
)
from app.models.post import Post, PostStatus
from app.models.channel import ContentTypeModel

sync_engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
SyncSession = sessionmaker(bind=sync_engine)


@shared_task(name="app.tasks.content_tasks.fetch_reddit_content")
def fetch_reddit_content():
    from app.services.content.reddit import RedditSource
    import asyncio

    source = RedditSource()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        posts = loop.run_until_complete(source.fetch_posts("interestingasfuck", limit=10))

        db = SyncSession()
        try:
            for post_data in posts:
                existing = db.query(Post).filter(Post.source_url == post_data["url"]).first()

                if existing:
                    continue

                processed = loop.run_until_complete(
                    source.process_for_post(post_data, translate=True, rewrite=True)
                )

                content_type = (
                    db.query(ContentTypeModel).filter(ContentTypeModel.type == "reddit").first()
                )

                post = Post(
                    channel_id=1,
                    content_type_id=content_type.id if content_type else None,
                    title=processed.get("title"),
                    body=processed["body"],
                    source_url=processed.get("source_url"),
                    source_title=processed.get("source_title"),
                    media_urls=processed.get("media_urls"),
                    ai_metadata=processed.get("ai_metadata"),
                    status=PostStatus.PENDING,
                    generated_at=datetime.utcnow(),
                )

                db.add(post)

            db.commit()
            return {"generated": generated}
        finally:
            db.close()
    finally:
        loop.close()


@shared_task(name="app.tasks.content_tasks.generate_moscow_facts")
def generate_moscow_facts():
    from app.services.content.moscow_facts import MoscowFactsSource
    import asyncio

    source = MoscowFactsSource()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        facts = loop.run_until_complete(source.generate_multiple(count=3, use_ai=True))

        db = SyncSession()
        try:
            content_type = (
                db.query(ContentTypeModel).filter(ContentTypeModel.type == "moscow_facts").first()
            )

            generated = 0
            for fact in facts:
                post = Post(
                    channel_id=1,
                    content_type_id=content_type.id if content_type else None,
                    title=fact["topic"],
                    body=fact["body"],
                    status=PostStatus.PENDING,
                    generated_at=datetime.utcnow(),
                    ai_metadata={
                        "fact_type": fact["type"],
                        "generated_with_ai": fact.get("generated_with_ai", False),
                    },
                )
                db.add(post)
                generated += 1

            db.commit()
            return {"generated": generated}
        finally:
            db.close()
    finally:
        loop.close()


@shared_task(name="app.tasks.content_tasks.generate_horoscopes")
def generate_horoscopes():
    from app.services.content.horoscope import HoroscopeSource
    import asyncio

    source = HoroscopeSource()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        horoscopes = loop.run_until_complete(source.generate_all_signs(use_ai=True))

        db = SyncSession()
        try:
            content_type = (
                db.query(ContentTypeModel).filter(ContentTypeModel.type == "horoscope").first()
            )

            for h in horoscopes:
                post = Post(
                    channel_id=1,
                    content_type_id=content_type.id if content_type else None,
                    title=f"Гороскоп: {h['sign']} на {h['date']}",
                    body=h["body"],
                    status=PostStatus.PENDING,
                    generated_at=datetime.utcnow(),
                    ai_metadata={"generated_with_ai": h.get("generated_with_ai", False)},
                )
                db.add(post)

            db.commit()
            return {"generated": len(horoscopes)}
        finally:
            db.close()
    finally:
        loop.close()


@shared_task(name="app.tasks.content_tasks.generate_animal_facts")
def generate_animal_facts():
    from app.services.content.animal_facts import AnimalFactsSource
    import asyncio

    source = AnimalFactsSource()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        facts = loop.run_until_complete(source.generate_multiple(count=3, use_ai=True))

        db = SyncSession()
        try:
            content_type = (
                db.query(ContentTypeModel).filter(ContentTypeModel.type == "animal_facts").first()
            )

            for fact in facts:
                post = Post(
                    channel_id=1,
                    content_type_id=content_type.id if content_type else None,
                    title=f"Факт о {fact['animal']}",
                    body=fact["body"],
                    status=PostStatus.PENDING,
                    generated_at=datetime.utcnow(),
                    ai_metadata={"generated_with_ai": fact.get("generated_with_ai", False)},
                )
                db.add(post)

            db.commit()
            return {"generated": len(facts)}
        finally:
            db.close()
    finally:
        loop.close()


@shared_task(name="app.tasks.content_tasks.fetch_news_content")
def fetch_news_content():
    from app.services.content.news import NewsSource
    import asyncio

    source = NewsSource()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        news_items = loop.run_until_complete(source.fetch_all_sources(limit_per_source=5))

        db = SyncSession()
        try:
            content_type = (
                db.query(ContentTypeModel).filter(ContentTypeModel.type == "news").first()
            )

            count = 0
            for item in news_items:
                existing = db.query(Post).filter(Post.source_url == item.get("link")).first()

                if existing:
                    continue

                processed = loop.run_until_complete(source.process_news(item, summarize=True))

                post = Post(
                    channel_id=1,
                    content_type_id=content_type.id if content_type else None,
                    title=processed["title"],
                    body=processed["body"],
                    source_url=processed.get("source_url"),
                    status=PostStatus.PENDING,
                    generated_at=datetime.utcnow(),
                    ai_metadata={"source": processed.get("source_name")},
                )
                db.add(post)
                count += 1

            db.commit()
            return {"fetched": count}
        finally:
            db.close()
    finally:
        loop.close()


@shared_task(name="app.tasks.content_tasks.generate_city_content")
def generate_city_content():
    from app.services.content.city import CitySource, CITIES_CONFIG
    from app.config import settings
    import asyncio

    source = CitySource(weather_api_key=settings.OPENWEATHER_API_KEY)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        db = SyncSession()
        try:
            content_type = (
                db.query(ContentTypeModel).filter(ContentTypeModel.type == "city").first()
            )

            generated = 0
            for city_key in CITIES_CONFIG.keys():
                post_data = loop.run_until_complete(
                    source.generate_city_post(city_key, include_weather=True, include_greeting=True)
                )

                if "error" in post_data:
                    continue

                post = Post(
                    channel_id=1,
                    content_type_id=content_type.id if content_type else None,
                    title=f"Новости {post_data['city_name']}",
                    body=post_data["body"],
                    status=PostStatus.PENDING,
                    generated_at=datetime.utcnow(),
                    ai_metadata={
                        "city": city_key,
                        "weather_included": post_data.get("weather_included"),
                    },
                )
                db.add(post)
                generated += 1

            db.commit()
            return {"generated": generated}
        finally:
            db.close()
    finally:
        loop.close()


@shared_task(name="app.tasks.content_tasks.generate_affiliate_posts")
def generate_affiliate_posts():
    from app.services.content.affiliate import AffiliateSource
    from app.models.analytics import AffiliateProduct
    import asyncio

    source = AffiliateSource()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        db = SyncSession()
        try:
            products = (
                db.query(AffiliateProduct).filter(AffiliateProduct.is_active == True).limit(5).all()
            )

            for product in products:
                source.add_product(
                    name=product.name,
                    description=product.description or "",
                    ref_url=product.ref_url,
                    category=product.category,
                    keywords=[],
                )

            content_type = (
                db.query(ContentTypeModel).filter(ContentTypeModel.type == "affiliate").first()
            )

            generated = 0
            for _ in range(min(3, len(products))):
                post_data = loop.run_until_complete(source.generate_post(use_ai=True))

                if not post_data:
                    continue

                post = Post(
                    channel_id=1,
                    content_type_id=content_type.id if content_type else None,
                    title=post_data["product_name"],
                    body=post_data["body"],
                    status=PostStatus.PENDING,
                    generated_at=datetime.utcnow(),
                    ai_metadata={
                        "product_category": post_data.get("product_category"),
                        "ref_url": post_data["ref_url"],
                        "generated_with_ai": post_data.get("generated_with_ai", False),
                    },
                )
                db.add(post)
                generated += 1

            db.commit()
            return {"generated": generated}
        finally:
            db.close()
    finally:
        loop.close()
