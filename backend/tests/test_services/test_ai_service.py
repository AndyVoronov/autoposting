import pytest
from unittest.mock import AsyncMock, patch


class TestAIServiceChat:
    @pytest.mark.asyncio
    async def test_chat_success(self, mock_glm_api):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        result = await service.chat("Hello", "You are helpful")
        assert result == "AI generated response"

    @pytest.mark.asyncio
    async def test_chat_no_api_key(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = None

        result = await service.chat("Hello")
        assert result is None

    @pytest.mark.asyncio
    async def test_chat_with_system_prompt(self, mock_glm_api):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        result = await service.chat("Hello", system_prompt="You are a helpful assistant")
        assert result is not None

    @pytest.mark.asyncio
    async def test_chat_custom_params(self, mock_glm_api):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        result = await service.chat("Hello", temperature=0.5, max_tokens=1000)
        assert result is not None


class TestAIServiceTranslate:
    @pytest.mark.asyncio
    async def test_translate_to_russian_success(self, mock_glm_api):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Переведенный текст"
            result = await service.translate_to_russian("Hello world")
            assert result == "Переведенный текст"

    @pytest.mark.asyncio
    async def test_translate_to_russian_no_key(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = None

        result = await service.translate_to_russian("Hello")
        assert result is None


class TestAIServiceRewrite:
    @pytest.mark.asyncio
    async def test_rewrite_text_success(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Переписанный текст"
            result = await service.rewrite_text("Original text", "интересный")
            assert result == "Переписанный текст"


class TestAIServiceHoroscope:
    @pytest.mark.asyncio
    async def test_generate_horoscope(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Сегодня отличный день для новых начинаний!"
            result = await service.generate_horoscope("Овен", "01.01.2024")
            assert "начинаний" in result


class TestAIServiceAnimalFact:
    @pytest.mark.asyncio
    async def test_generate_animal_fact(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Киты могут петь!"
            result = await service.generate_animal_fact("кит")
            assert result is not None


class TestAIServiceSummarize:
    @pytest.mark.asyncio
    async def test_summarize_news(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Краткая сводка новостей"
            result = await service.summarize_news("Длинный текст новости...")
            assert "сводка" in result


class TestAIServiceAffiliate:
    @pytest.mark.asyncio
    async def test_generate_affiliate_post(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Отличный товар для вас!"
            result = await service.generate_affiliate_post("Товар", "Описание", ["тег1"])
            assert result is not None


class TestAIServiceImprove:
    @pytest.mark.asyncio
    async def test_improve_text(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Улучшенный текст"
            result = await service.improve_text("Простой текст")
            assert result == "Улучшенный текст"


class TestAIServiceShorten:
    @pytest.mark.asyncio
    async def test_shorten_text(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Сокращенный"
            result = await service.shorten_text("Очень длинный текст", max_chars=100)
            assert result == "Сокращенный"


class TestAIServiceRewriteForPost:
    @pytest.mark.asyncio
    async def test_rewrite_text_for_post(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Переписанный для поста"
            result = await service.rewrite_text_for_post("Оригинальный текст")
            assert result == "Переписанный для поста"


class TestAIServiceCensorship:
    @pytest.mark.asyncio
    async def test_check_censorship_safe(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = '{"safe": true, "reasons": [], "suggestion": null}'
            result = await service.check_censorship("Безопасный текст")
            assert result["safe"] is True

    @pytest.mark.asyncio
    async def test_check_censorship_unsafe(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = (
                '{"safe": false, "reasons": ["Причина 1"], "suggestion": "Исправить"}'
            )
            result = await service.check_censorship("Опасный текст")
            assert result["safe"] is False
            assert len(result["reasons"]) == 1

    @pytest.mark.asyncio
    async def test_check_censorship_invalid_json(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = "Invalid JSON response"
            result = await service.check_censorship("Text")
            assert result["safe"] is True

    @pytest.mark.asyncio
    async def test_check_censorship_no_response(self):
        from app.services.ai.glm import AIService

        service = AIService()
        service.api_key = "test-key"

        with patch.object(service, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = None
            result = await service.check_censorship("Text")
            assert result["safe"] is True
