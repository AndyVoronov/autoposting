import pytest


class TestCensorshipRulesList:
    async def test_get_rules_empty(self, client, auth_header):
        response = await client.get("/api/censorship/rules", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_rules_with_data(self, client, auth_header, sample_censorship_rule):
        response = await client.get("/api/censorship/rules", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["pattern"] == "forbidden_word"

    async def test_get_rules_unauthorized(self, client):
        response = await client.get("/api/censorship/rules")
        assert response.status_code == 403


class TestCensorshipRuleCreate:
    async def test_create_banned_word_rule(self, client, auth_header):
        response = await client.post(
            "/api/censorship/rules",
            json={
                "pattern": "bad_word",
                "pattern_type": "word",
                "rule_type": "banned",
                "category": "profanity",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pattern"] == "bad_word"
        assert data["rule_type"] == "banned"

    async def test_create_warn_word_rule(self, client, auth_header):
        response = await client.post(
            "/api/censorship/rules",
            json={
                "pattern": "politics",
                "pattern_type": "word",
                "rule_type": "warn",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["rule_type"] == "warn"

    async def test_create_regex_rule(self, client, auth_header):
        response = await client.post(
            "/api/censorship/rules",
            json={
                "pattern": r"\d{16}",
                "pattern_type": "regex",
                "rule_type": "banned",
                "category": "personal_data",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["pattern_type"] == "regex"

    async def test_create_auto_edit_rule(self, client, auth_header):
        response = await client.post(
            "/api/censorship/rules",
            json={
                "pattern": "bad",
                "pattern_type": "word",
                "rule_type": "auto_edit",
                "replacement": "good",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["rule_type"] == "auto_edit"


class TestCensorshipRuleDelete:
    async def test_delete_rule(self, client, auth_header, sample_censorship_rule):
        response = await client.delete(
            f"/api/censorship/rules/{sample_censorship_rule.id}", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

    async def test_delete_rule_not_found(self, client, auth_header):
        response = await client.delete("/api/censorship/rules/9999", headers=auth_header)
        assert response.status_code == 404


class TestCensorshipCheck:
    async def test_check_clean_text(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/censorship/check",
            json={"text": "This is a clean and safe text."},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is True
        assert data["action"] == "allow"

    async def test_check_banned_word(self, client, auth_header):
        response = await client.post(
            "/api/censorship/check",
            json={"text": "This contains протест in it."},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is False
        assert data["action"] == "reject"

    async def test_check_warn_word(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/censorship/check",
            json={"text": "This is about политика."},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action"] in ["warn", "allow"]

    async def test_check_custom_rule(
        self, client, auth_header, sample_censorship_rule, mock_ai_service
    ):
        response = await client.post(
            "/api/censorship/check",
            json={"text": "This has forbidden_word inside."},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is False

    async def test_check_empty_text(self, client, auth_header, mock_ai_service):
        response = await client.post(
            "/api/censorship/check",
            json={"text": ""},
            headers=auth_header,
        )
        assert response.status_code == 200
