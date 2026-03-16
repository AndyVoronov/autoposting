import pytest
from datetime import datetime


class TestUserModel:
    def test_user_creation(self, db):
        from app.models.user import User

        user = User(
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
        )
        db.add(user)
        db.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.is_active is True

    def test_user_default_is_active(self, db):
        from app.models.user import User

        user = User(
            username="testuser2",
            password_hash="hashed",
        )

        assert user.is_active is True

    def test_user_created_at_default(self):
        from app.models.user import User

        user = User(username="test", password_hash="hash")

        assert user.created_at is not None


class TestChannelModel:
    def test_channel_creation(self, db):
        from app.models.channel import Channel, Platform

        channel = Channel(
            name="Test Channel",
            slug="test-channel",
            platform=Platform.TELEGRAM,
            config={"chat_id": "@test"},
        )
        db.add(channel)
        db.commit()

        assert channel.id is not None
        assert channel.platform == Platform.TELEGRAM

    def test_channel_default_values(self):
        from app.models.channel import Channel, Platform

        channel = Channel(name="Test", slug="test")

        assert channel.platform == Platform.TELEGRAM
        assert channel.is_active is True

    def test_channel_unique_slug(self, db):
        from app.models.channel import Channel, Platform

        channel1 = Channel(name="Channel 1", slug="unique-slug", platform=Platform.TELEGRAM)
        channel2 = Channel(name="Channel 2", slug="unique-slug", platform=Platform.VK)

        db.add(channel1)
        db.commit()

        db.add(channel2)

        with pytest.raises(Exception):
            db.commit()

    def test_channel_posts_relationship(self, db, sample_post):
        from app.models.channel import Channel

        result = db.execute("SELECT * FROM channels WHERE id = ?", (sample_post.channel_id,))
        channel = result.fetchone()

        assert channel is not None


class TestPostModel:
    def test_post_creation(self, db, sample_channel):
        from app.models.post import Post, PostStatus

        post = Post(
            channel_id=sample_channel.id,
            title="Test Title",
            body="Test body content",
            status=PostStatus.DRAFT,
        )
        db.add(post)
        db.commit()

        assert post.id is not None
        assert post.status == PostStatus.DRAFT

    def test_post_default_status(self, sample_channel):
        from app.models.post import Post, PostStatus

        post = Post(channel_id=sample_channel.id, body="Content")

        assert post.status == PostStatus.DRAFT

    def test_post_status_enum_values(self):
        from app.models.post import PostStatus

        assert PostStatus.DRAFT.value == "draft"
        assert PostStatus.PENDING.value == "pending"
        assert PostStatus.APPROVED.value == "approved"
        assert PostStatus.SCHEDULED.value == "scheduled"
        assert PostStatus.PUBLISHED.value == "published"
        assert PostStatus.FAILED.value == "failed"
        assert PostStatus.REJECTED.value == "rejected"

    def test_post_media_urls(self, db, sample_channel):
        from app.models.post import Post

        post = Post(
            channel_id=sample_channel.id,
            body="Content",
            media_urls=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        )
        db.add(post)
        db.commit()

        assert len(post.media_urls) == 2

    def test_post_ai_metadata(self, db, sample_channel):
        from app.models.post import Post

        post = Post(
            channel_id=sample_channel.id,
            body="Content",
            ai_metadata={"translated": True, "source": "reddit"},
        )
        db.add(post)
        db.commit()

        assert post.ai_metadata["translated"] is True


class TestContentTypeModel:
    def test_content_type_creation(self, db):
        from app.models.channel import ContentTypeModel, ContentType

        ct = ContentTypeModel(
            name="Reddit Posts",
            type=ContentType.REDDIT,
            description="Posts from Reddit",
        )
        db.add(ct)
        db.commit()

        assert ct.id is not None
        assert ct.type == ContentType.REDDIT

    def test_content_type_enum_values(self):
        from app.models.channel import ContentType

        assert ContentType.REDDIT.value == "reddit"
        assert ContentType.HOROSCOPE.value == "horoscope"
        assert ContentType.ANIMAL_FACTS.value == "animal_facts"
        assert ContentType.NEWS.value == "news"
        assert ContentType.CITY.value == "city"
        assert ContentType.AFFILIATE.value == "affiliate"
        assert ContentType.CUSTOM.value == "custom"


class TestCensorshipRuleModel:
    def test_censorship_rule_creation(self, db):
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern="bad_word",
            pattern_type="word",
            rule_type="banned",
            category="profanity",
        )
        db.add(rule)
        db.commit()

        assert rule.id is not None
        assert rule.is_active is True

    def test_censorship_rule_with_replacement(self, db):
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern="bad",
            pattern_type="word",
            rule_type="auto_edit",
            replacement="good",
        )
        db.add(rule)
        db.commit()

        assert rule.replacement == "good"


class TestAffiliateProductModel:
    def test_product_creation(self, db):
        from app.models.analytics import AffiliateProduct

        product = AffiliateProduct(
            name="Test Product",
            category="electronics",
            ref_url="https://example.com/product",
            description="A test product",
        )
        db.add(product)
        db.commit()

        assert product.id is not None
        assert product.is_active is True

    def test_product_with_keywords(self, db):
        from app.models.analytics import AffiliateProduct

        product = AffiliateProduct(
            name="Product",
            ref_url="https://example.com/p",
            keywords=["tech", "gadget"],
        )
        db.add(product)
        db.commit()

        assert len(product.keywords) == 2


class TestAnalyticsModel:
    def test_analytics_creation(self, db, sample_post):
        from app.models.analytics import Analytics

        analytics = Analytics(
            post_id=sample_post.id,
            platform="telegram",
            views=1000,
            likes=50,
            shares=10,
            comments=5,
            clicks=100,
        )
        db.add(analytics)
        db.commit()

        assert analytics.id is not None
        assert analytics.views == 1000


class TestPublishQueueModel:
    def test_queue_item_creation(self, db, sample_post):
        from app.models.post import PublishQueue
        from app.models.channel import Platform

        item = PublishQueue(
            post_id=sample_post.id,
            platform=Platform.TELEGRAM,
            scheduled_at=datetime.utcnow(),
        )
        db.add(item)
        db.commit()

        assert item.id is not None
        assert item.status == "pending"
        assert item.attempts == 0
        assert item.max_attempts == 3
