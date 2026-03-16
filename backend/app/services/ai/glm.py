import httpx
from typing import Optional
from app.config import settings


class AIService:
    def __init__(self):
        self.api_url = settings.GLM_API_URL
        self.api_key = settings.GLM_API_KEY
        self.model = "glm-4-flash"

    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        if not self.api_key:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI Service error: {e}")
            return None

    async def translate_to_russian(self, text: str) -> Optional[str]:
        return await self.chat(
            prompt=text,
            system_prompt="Переведи следующий текст на русский язык. Сохрани стиль и смысл оригинала. Отвечай только переводом.",
            temperature=0.3,
        )

    async def rewrite_text(self, text: str, style: str = "интересный") -> Optional[str]:
        return await self.chat(
            prompt=f"Перепиши следующий текст в {style} стиле, сохранив смысл:\n\n{text}",
            system_prompt="Ты профессиональный копирайтер для социальных сетей. Переписывай текст интересно и engaging.",
            temperature=0.8,
        )

    async def generate_horoscope(self, sign: str, date: str) -> Optional[str]:
        return await self.chat(
            prompt=f"Напиши гороскоп для знака {sign} на {date}. Включи: общее настроение, любовь, карьеру, здоровье. Будь позитивным и вдохновляющим.",
            system_prompt="Ты профессиональный астролог. Пиши гороскопы интересно и позитивно, 3-4 предложения.",
            temperature=0.9,
            max_tokens=500,
        )

    async def generate_animal_fact(self, animal: str) -> Optional[str]:
        return await self.chat(
            prompt=f"Напиши один интересный и удивительный факт о {animal}.",
            system_prompt="Ты эксперт по животным. Пиши кратко (2-3 предложения) и интересно.",
            temperature=0.8,
            max_tokens=300,
        )

    async def summarize_news(self, text: str) -> Optional[str]:
        return await self.chat(
            prompt=f"Сделай краткую выжимку новости (2-3 предложения):\n\n{text}",
            system_prompt="Ты новостной редактор. Пиши объективно и нейтрально.",
            temperature=0.3,
            max_tokens=500,
        )

    async def generate_affiliate_post(
        self, product_name: str, description: str, keywords: list[str]
    ) -> Optional[str]:
        keywords_str = ", ".join(keywords) if keywords else ""
        return await self.chat(
            prompt=f"""Создай пост для соцсетей о товаре: {product_name}
Описание: {description}
Ключевые слова: {keywords_str}

Встрой призыв к действию естественно. Не пиши "купите", "закажите". Используй мягкие формулировки.""",
            system_prompt="Ты SMM-специалист. Пиши нативно, не навязчиво. Используй эмодзи умеренно.",
            temperature=0.8,
            max_tokens=500,
        )

    async def improve_text(self, text: str) -> Optional[str]:
        return await self.chat(
            prompt=f"Улучши следующий текст, сделай его более интересным и engaging:\n\n{text}",
            system_prompt="Ты профессиональный SMM-специалист. Улучшай текст, сохраняя его смысл. Добавляй эмодзи умеренно.",
            temperature=0.7,
            max_tokens=2000,
        )

    async def shorten_text(self, text: str, max_chars: int = 500) -> Optional[str]:
        return await self.chat(
            prompt=f"Сократи текст до примерно {max_chars} символов, сохранив главный смысл:\n\n{text}",
            system_prompt="Ты редактор соцсетей. Сокращай текст, убирая лишнее, но сохраняя суть.",
            temperature=0.5,
            max_tokens=1000,
        )

    async def rewrite_text_for_post(self, text: str) -> Optional[str]:
        return await self.chat(
            prompt=f"Перепиши текст другими словами, сохранив смысл:\n\n{text}",
            system_prompt="Ты копирайтер. Переписывай текст интересно, уникально, избегая плагиата.",
            temperature=0.8,
            max_tokens=2000,
        )

    async def check_censorship(self, text: str) -> dict:
        response = await self.chat(
            prompt=f"""Проверь текст на наличие запрещённого в РФ контента:
- Политика, протесты, оппозиция
- Критика властей
- Военные действия (кроме официальной позиции)
- Санкции против РФ

Текст:
{text}

Ответь в формате JSON:
{{"safe": true/false, "reasons": ["причина1", "причина2"], "suggestion": "как исправить"}}""",
            system_prompt="Ты цензор. Отвечай только JSON без markdown.",
            temperature=0.1,
            max_tokens=500,
        )

        if response:
            try:
                import json

                return json.loads(response)
            except:
                pass

        return {"safe": True, "reasons": [], "suggestion": None}


ai_service = AIService()
