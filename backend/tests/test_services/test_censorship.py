import pytest
from unittest.mock import AsyncMock, patch


class TestCensorshipServiceInit:
    def test_init(self, db):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        assert service.db == db
        assert service._rules_cache is None


class TestCensorshipServiceGetRules:
    @pytest.mark.asyncio
    async def test_get_rules_empty(self, db):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        rules = await service.get_rules()
        assert rules == []

    @pytest.mark.asyncio
    async def test_get_rules_with_data(self, db, sample_censorship_rule):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        rules = await service.get_rules()
        assert len(rules) == 1
        assert rules[0].pattern == "forbidden_word"

    @pytest.mark.asyncio
    async def test_get_rules_cache(self, db, sample_censorship_rule):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        rules1 = await service.get_rules()
        rules2 = await service.get_rules()
        assert rules1 == rules2

    @pytest.mark.asyncio
    async def test_clear_cache(self, db):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        await service.get_rules()
        service.clear_cache()
        assert service._rules_cache is None


class TestCensorshipServiceCheckText:
    @pytest.mark.asyncio
    async def test_check_clean_text(self, db, mock_ai_service):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        result = await service.check_text("This is a clean text")

        assert result["passed"] is True
        assert result["action"] == "allow"
        assert len(result["matched_rules"]) == 0

    @pytest.mark.asyncio
    async def test_check_banned_default_word(self, db):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        result = await service.check_text("Этот текст содержит протест")

        assert result["passed"] is False
        assert result["action"] == "reject"
        assert len(result["matched_rules"]) > 0

    @pytest.mark.asyncio
    async def test_check_warn_default_word(self, db, mock_ai_service):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        result = await service.check_text("Этот текст о политика")

        assert result["action"] in ["warn", "allow"]

    @pytest.mark.asyncio
    async def test_check_custom_rule_banned(self, db, sample_censorship_rule, mock_ai_service):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        result = await service.check_text("This has forbidden_word in it")

        assert result["passed"] is False
        assert result["action"] == "reject"

    @pytest.mark.asyncio
    async def test_check_regex_rule(self, db, mock_ai_service):
        from app.services.censorship.service import CensorshipService
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern=r"\b\d{3}-\d{2}-\d{4}\b",
            pattern_type="regex",
            rule_type="banned",
            category="personal_data",
            is_active=True,
        )
        db.add(rule)
        await db.commit()

        service = CensorshipService(db)
        result = await service.check_text("SSN: 123-45-6789")

        assert result["passed"] is False

    @pytest.mark.asyncio
    async def test_check_invalid_regex(self, db, mock_ai_service):
        from app.services.censorship.service import CensorshipService
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern="[invalid(regex",
            pattern_type="regex",
            rule_type="banned",
            is_active=True,
        )
        db.add(rule)
        await db.commit()

        service = CensorshipService(db)
        result = await service.check_text("Some text")

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_check_with_post_id(self, db, mock_ai_service, sample_post):
        from app.services.censorship.service import CensorshipService

        service = CensorshipService(db)
        result = await service.check_text("Clean text", post_id=sample_post.id)

        assert result["passed"] is True


class TestCensorshipServiceAutoEdit:
    @pytest.mark.asyncio
    async def test_auto_edit_word(self, db):
        from app.services.censorship.service import CensorshipService
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern="bad",
            pattern_type="word",
            rule_type="auto_edit",
            replacement="good",
            is_active=True,
        )
        db.add(rule)
        await db.commit()

        service = CensorshipService(db)
        result = await service.auto_edit("This is bad text")

        assert "bad" not in result.lower()
        assert "good" in result.lower()

    @pytest.mark.asyncio
    async def test_auto_edit_regex(self, db):
        from app.services.censorship.service import CensorshipService
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern=r"\b\d{3}-\d{2}-\d{4}\b",
            pattern_type="regex",
            rule_type="auto_edit",
            replacement="[REDACTED]",
            is_active=True,
        )
        db.add(rule)
        await db.commit()

        service = CensorshipService(db)
        result = await service.auto_edit("SSN: 123-45-6789")

        assert "123-45-6789" not in result
        assert "[REDACTED]" in result

    @pytest.mark.asyncio
    async def test_auto_edit_no_replacement(self, db):
        from app.services.censorship.service import CensorshipService
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern="test",
            pattern_type="word",
            rule_type="auto_edit",
            replacement=None,
            is_active=True,
        )
        db.add(rule)
        await db.commit()

        service = CensorshipService(db)
        result = await service.auto_edit("This is test text")

        assert "test" in result

    @pytest.mark.asyncio
    async def test_auto_edit_invalid_regex(self, db):
        from app.services.censorship.service import CensorshipService
        from app.models.censorship import CensorshipRule

        rule = CensorshipRule(
            pattern="[invalid(regex",
            pattern_type="regex",
            rule_type="auto_edit",
            replacement="replaced",
            is_active=True,
        )
        db.add(rule)
        await db.commit()

        service = CensorshipService(db)
        result = await service.auto_edit("Some text")

        assert result == "Some text"


class TestCheckCensorshipFunction:
    @pytest.mark.asyncio
    async def test_check_censorship_function(self, db, mock_ai_service):
        from app.services.censorship import check_censorship

        result = await check_censorship(db, "Clean text")

        assert "passed" in result
        assert "action" in result
        assert "matched_rules" in result
