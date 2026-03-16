import pytest
from unittest.mock import AsyncMock, patch
from datetime import date


class TestHoroscopeSourceInit:
    def test_init(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        assert source.use_ai is True


class TestHoroscopeSourceGetZodiacSign:
    def test_get_zodiac_sign_aries(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 4, 1))
        assert result == "Овен"

    def test_get_zodiac_sign_taurus(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 5, 1))
        assert result == "Телец"

    def test_get_zodiac_sign_gemini(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 6, 1))
        assert result == "Близнецы"

    def test_get_zodiac_sign_cancer(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 7, 1))
        assert result == "Рак"

    def test_get_zodiac_sign_leo(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 8, 1))
        assert result == "Лев"

    def test_get_zodiac_sign_virgo(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 9, 1))
        assert result == "Дева"

    def test_get_zodiac_sign_libra(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 10, 1))
        assert result == "Весы"

    def test_get_zodiac_sign_scorpio(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 11, 1))
        assert result == "Скорпион"

    def test_get_zodiac_sign_sagittarius(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 12, 1))
        assert result == "Стрелец"

    def test_get_zodiac_sign_capricorn(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 1, 1))
        assert result == "Козерог"

    def test_get_zodiac_sign_aquarius(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 2, 1))
        assert result == "Водолей"

    def test_get_zodiac_sign_pisces(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_zodiac_sign(date(2000, 3, 1))
        assert result == "Рыбы"


class TestHoroscopeSourceGenerateDailyHoroscope:
    @pytest.mark.asyncio
    async def test_generate_daily_horoscope_with_ai(self, mock_ai_service):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()

        with patch.object(source, "use_ai", True):
            with patch("app.services.content.horoscope.ai_service") as mock_ai:
                mock_ai.generate_horoscope = AsyncMock(return_value="Гороскоп для Овна")

                result = await source.generate_daily_horoscope(
                    "Овен", date(2024, 1, 15), use_ai=True
                )

                assert result["sign"] == "Овен"
                assert "Овен" in result["body"]
                assert result["generated_with_ai"] is True

    @pytest.mark.asyncio
    async def test_generate_daily_horoscope_without_ai(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()

        result = await source.generate_daily_horoscope("Овен", date(2024, 1, 15), use_ai=False)

        assert result["sign"] == "Овен"
        assert result["generated_with_ai"] is False
        assert "emoji" in result

    @pytest.mark.asyncio
    async def test_generate_daily_horoscope_fallback(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()

        with patch("app.services.content.horoscope.ai_service") as mock_ai:
            mock_ai.generate_horoscope = AsyncMock(return_value=None)

            result = await source.generate_daily_horoscope("Телец", date(2024, 1, 15), use_ai=True)

            assert result["sign"] == "Телец"
            assert result["generated_with_ai"] is False


class TestHoroscopeSourceGenerateAllSigns:
    @pytest.mark.asyncio
    async def test_generate_all_signs(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()

        results = await source.generate_all_signs(date(2024, 1, 15), use_ai=False)

        assert len(results) == 12
        signs = [r["sign"] for r in results]
        assert "Овен" in signs
        assert "Телец" in signs
        assert "Рыбы" in signs


class TestHoroscopeSourceGetSignByDate:
    def test_get_sign_by_date_capricorn(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_sign_by_date(12, 25)
        assert result == "Козерог"

    def test_get_sign_by_date_january(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_sign_by_date(1, 15)
        assert result == "Козерог"

    def test_get_sign_by_date_invalid(self):
        from app.services.content.horoscope import HoroscopeSource

        source = HoroscopeSource()
        result = source.get_sign_by_date(13, 32)
        assert result is None
