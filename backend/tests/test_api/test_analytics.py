import pytest
from datetime import datetime, timedelta


class TestAnalyticsDashboard:
    async def test_get_dashboard_stats_empty(self, client, auth_header):
        response = await client.get("/api/analytics/dashboard", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["total_channels"] == 0
        assert data["total_posts"] == 0
        assert data["pending_posts"] == 0
        assert data["published_today"] == 0

    async def test_get_dashboard_stats_with_data(
        self, client, auth_header, sample_channel, sample_post, db
    ):
        response = await client.get("/api/analytics/dashboard", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["total_channels"] >= 1
        assert data["total_posts"] >= 1

    async def test_get_dashboard_stats_unauthorized(self, client):
        response = await client.get("/api/analytics/dashboard")
        assert response.status_code == 403


class TestAnalyticsPostStats:
    async def test_get_post_stats(self, client, auth_header, sample_post):
        response = await client.get(f"/api/analytics/posts/{sample_post.id}", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["post_id"] == sample_post.id
        assert "views" in data
        assert "likes" in data

    async def test_get_post_stats_not_found(self, client, auth_header):
        response = await client.get("/api/analytics/posts/9999", headers=auth_header)
        assert response.status_code == 404

    async def test_get_post_stats_with_analytics(self, client, auth_header, sample_post, db):
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
        await db.commit()

        response = await client.get(f"/api/analytics/posts/{sample_post.id}", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["views"] == 1000
        assert data["likes"] == 50


class TestAnalyticsDaily:
    async def test_get_daily_stats(self, client, auth_header):
        response = await client.get("/api/analytics/daily?days=7", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 7
        for day in data:
            assert "date" in day
            assert "posts" in day
            assert "views" in day
            assert "clicks" in day

    async def test_get_daily_stats_custom_days(self, client, auth_header):
        response = await client.get("/api/analytics/daily?days=14", headers=auth_header)
        assert response.status_code == 200
        assert len(response.json()) == 14


class TestAnalyticsTopPosts:
    async def test_get_top_posts_empty(self, client, auth_header):
        response = await client.get("/api/analytics/top-posts", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_top_posts_with_data(
        self, client, auth_header, sample_channel, sample_post, db
    ):
        from app.models.analytics import Analytics

        analytics = Analytics(
            post_id=sample_post.id,
            platform="telegram",
            views=5000,
            likes=100,
        )
        db.add(analytics)
        await db.commit()

        response = await client.get("/api/analytics/top-posts", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10

    async def test_get_top_posts_with_limit(self, client, auth_header):
        response = await client.get("/api/analytics/top-posts?limit=5", headers=auth_header)
        assert response.status_code == 200


class TestReferralClicks:
    async def test_get_referral_clicks_empty(self, client, auth_header):
        response = await client.get("/api/analytics/referral-clicks", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_referral_clicks_with_data(
        self, client, auth_header, sample_product, sample_channel, db
    ):
        from app.models.analytics import AffiliateClick

        click = AffiliateClick(
            product_id=sample_product.id,
            post_id=None,
            channel_id=sample_channel.id,
        )
        db.add(click)
        await db.commit()

        response = await client.get("/api/analytics/referral-clicks", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
