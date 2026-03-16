import pytest


class TestAIImprove:
    async def test_improve_text(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/ai/improve",
            json={"text": "This is a simple text that needs improvement."},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] is not None

    async def test_improve_text_empty(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/ai/improve",
            json={"text": ""},
            headers=auth_header,
        )
        assert response.status_code == 200

    async def test_improve_text_unauthorized(self, client):
        response = await client.post(
            "/api/ai/improve",
            json={"text": "Some text"},
        )
        assert response.status_code == 403


class TestAIShorten:
    async def test_shorten_text(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/ai/shorten",
            json={"text": "This is a very long text that should be shortened.", "max_chars": 50},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_shorten_text_default_chars(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/ai/shorten",
            json={"text": "Some text"},
            headers=auth_header,
        )
        assert response.status_code == 200

    async def test_shorten_text_unauthorized(self, client):
        response = await client.post(
            "/api/ai/shorten",
            json={"text": "Some text"},
        )
        assert response.status_code == 403


class TestAIRewrite:
    async def test_rewrite_text(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/ai/rewrite",
            json={"text": "Original text that needs to be rewritten."},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_rewrite_text_empty(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/ai/rewrite",
            json={"text": ""},
            headers=auth_header,
        )
        assert response.status_code == 200

    async def test_rewrite_text_unauthorized(self, client):
        response = await client.post(
            "/api/ai/rewrite",
            json={"text": "Some text"},
        )
        assert response.status_code == 403
