from datetime import datetime, date
from typing import Optional
import random

from app.services.ai import ai_service


ZODIAC_SIGNS = [
    ("Овен", "Aries", (3, 21), (4, 19)),
    ("Телец", "Taurus", (4, 20), (5, 20)),
    ("Близнецы", "Gemini", (5, 21), (6, 20)),
    ("Рак", "Cancer", (6, 21), (7, 22)),
    ("Лев", "Leo", (7, 23), (8, 22)),
    ("Дева", "Virgo", (8, 23), (9, 22)),
    ("Весы", "Libra", (9, 23), (10, 22)),
    ("Скорпион", "Scorpio", (10, 23), (11, 21)),
    ("Стрелец", "Sagittarius", (11, 22), (12, 21)),
    ("Козерог", "Capricorn", (12, 22), (1, 19)),
    ("Водолей", "Aquarius", (1, 20), (2, 18)),
    ("Рыбы", "Pisces", (2, 19), (3, 20)),
]

MOOD_TEMPLATES = [
    "Сегодня звёзды на вашей стороне! ✨",
    "Энергия дня располагает к новым начинаниям 🌟",
    "Время для важных решений и смелых шагов 💫",
    "День обещает быть продуктивным и удачным 🍀",
    "Звёзды советуют быть внимательным к деталям 🔮",
]

LOVE_TEMPLATES = [
    "В личной жизни возможны приятные сюрпризы",
    "Отношения перейдут на новый уровень",
    "Одинокие могут встретить интересного человека",
    "Партнёр порадует вниманием и заботой",
    "Хороший день для романтических свиданий",
]

CAREER_TEMPLATES = [
    "На работе ждёт успех в текущих проектах",
    "Возможны интересные предложения по работе",
    "Хороший день для переговоров и встреч",
    "Финансовые вопросы решатся в вашу пользу",
    "Коллеги оценят ваши идеи и предложения",
]

HEALTH_TEMPLATES = [
    "Энергии хватит на все задуманные дела",
    "Не забывайте отдыхать и правильно питаться",
    "Хороший день для занятий спортом",
    "Слушайте свой организм и его потребности",
    "Уделите время прогулкам на свежем воздухе",
]

EMOJIS_BY_SIGN = {
    "Овен": "♈",
    "Телец": "♉",
    "Близнецы": "♊",
    "Рак": "♋",
    "Лев": "♌",
    "Дева": "♍",
    "Весы": "♎",
    "Скорпион": "♏",
    "Стрелец": "♐",
    "Козерог": "♑",
    "Водолей": "♒",
    "Рыбы": "♓",
}


class HoroscopeSource:
    def __init__(self):
        self.use_ai = True

    def get_zodiac_sign(self, birth_date: date) -> Optional[str]:
        month, day = birth_date.month, birth_date.day

        for sign_name, _, (start_m, start_d), (end_m, end_d) in ZODIAC_SIGNS:
            if start_m == end_m:
                if month == start_m and start_d <= day <= end_d:
                    return sign_name
            else:
                if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                    return sign_name

        return None

    async def generate_daily_horoscope(
        self,
        sign: str,
        target_date: Optional[date] = None,
        use_ai: bool = True,
    ) -> dict:
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%d.%m.%Y")
        emoji = EMOJIS_BY_SIGN.get(sign, "⭐")

        if use_ai and self.use_ai:
            ai_horoscope = await ai_service.generate_horoscope(sign, date_str)
            if ai_horoscope:
                return {
                    "sign": sign,
                    "emoji": emoji,
                    "date": date_str,
                    "body": f"{emoji} **{sign}** — {date_str}\n\n{ai_horoscope}",
                    "generated_with_ai": True,
                }

        # Fallback to template-based generation
        mood = random.choice(MOOD_TEMPLATES)
        love = random.choice(LOVE_TEMPLATES)
        career = random.choice(CAREER_TEMPLATES)
        health = random.choice(HEALTH_TEMPLATES)

        lucky_number = random.randint(1, 99)
        lucky_color = random.choice(
            ["красный", "синий", "зелёный", "жёлтый", "фиолетовый", "белый", "оранжевый"]
        )

        body = f"""{emoji} **{sign}** — {date_str}

{mood}

💫 **Личная жизнь:** {love}
💼 **Карьера:** {career}
💪 **Здоровье:** {health}

🍀 Счастливое число: {lucky_number}
🎨 Счастливый цвет: {lucky_color}"""

        return {
            "sign": sign,
            "emoji": emoji,
            "date": date_str,
            "body": body,
            "generated_with_ai": False,
        }

    async def generate_all_signs(
        self,
        target_date: Optional[date] = None,
        use_ai: bool = True,
    ) -> list[dict]:
        horoscopes = []

        for sign_name, _, _, _ in ZODIAC_SIGNS:
            horoscope = await self.generate_daily_horoscope(sign_name, target_date, use_ai)
            horoscopes.append(horoscope)

        return horoscopes

    def get_sign_by_date(self, month: int, day: int) -> Optional[str]:
        for sign_name, _, (start_m, start_d), (end_m, end_d) in ZODIAC_SIGNS:
            if start_m == 12 and end_m == 1:  # Capricorn
                if (month == 12 and day >= start_d) or (month == 1 and day <= end_d):
                    return sign_name
            elif start_m == end_m:
                if month == start_m and start_d <= day <= end_d:
                    return sign_name
            else:
                if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                    return sign_name

        return None


horoscope_source = HoroscopeSource()
