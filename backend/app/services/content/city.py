import httpx
from typing import Optional
from datetime import datetime
import random

from app.services.ai import ai_service


CITIES_CONFIG = {
    "moscow": {
        "name": "Москва",
        "timezone": "Europe/Moscow",
        "news_feeds": [
            "https://www.mos.ru/rss",
        ],
    },
    "spb": {
        "name": "Санкт-Петербург",
        "timezone": "Europe/Moscow",
        "news_feeds": [],
    },
    "novosibirsk": {
        "name": "Новосибирск",
        "timezone": "Asia/Novosibirsk",
        "news_feeds": [],
    },
    "ekaterinburg": {
        "name": "Екатеринбург",
        "timezone": "Asia/Yekaterinburg",
        "news_feeds": [],
    },
    "kazan": {
        "name": "Казань",
        "timezone": "Europe/Moscow",
        "news_feeds": [],
    },
}

EVENT_TEMPLATES = {
    "morning": [
        "Доброе утро, {city}! ☀️",
        "Начинаем день в {city}! 🌅",
    ],
    "day": [
        "Добрый день, {city}! 🌤",
        "Продолжаем день в {city}! ☀",
    ],
    "evening": [
        "Добрый вечер, {city}! 🌆",
        "Завершаем день в {city}! 🌇",
    ],
}

FUN_FACTS = [
    "В городе {city} сегодня отличный день для прогулок!",
    "Жители {city} могут порадоваться погоде!",
    "{city} продолжает радовать своих жителей!",
]


class CitySource:
    def __init__(self, weather_api_key: Optional[str] = None):
        self.weather_api_key = weather_api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_weather(self, city_key: str) -> Optional[dict]:
        if not self.weather_api_key:
            return None

        city_config = CITIES_CONFIG.get(city_key)
        if not city_config:
            return None

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": city_config["name"],
                        "appid": self.weather_api_key,
                        "units": "metric",
                        "lang": "ru",
                    },
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "temp": round(data["main"]["temp"]),
                    "feels_like": round(data["main"]["feels_like"]),
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind": round(data["wind"]["speed"]),
                }
        except Exception as e:
            print(f"Weather fetch error: {e}")
            return None

    def format_weather(self, weather: dict, city_name: str) -> str:
        return f"""🌡 **Погода в {city_name}**

Температура: {weather["temp"]}°C
Ощущается как: {weather["feels_like"]}°C
{weather["description"].capitalize()}
Влажность: {weather["humidity"]}%
Ветер: {weather["wind"]} м/с"""

    async def generate_city_post(
        self,
        city_key: str,
        include_weather: bool = True,
        include_greeting: bool = True,
    ) -> dict:
        city_config = CITIES_CONFIG.get(city_key)
        if not city_config:
            return {"error": f"City {city_key} not found"}

        city_name = city_config["name"]
        parts = []

        if include_greeting:
            hour = datetime.now().hour
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 18:
                time_of_day = "day"
            else:
                time_of_day = "evening"

            greeting = random.choice(EVENT_TEMPLATES[time_of_day]).format(city=city_name)
            parts.append(greeting)

        if include_weather and self.weather_api_key:
            weather = await self.get_weather(city_key)
            if weather:
                weather_text = self.format_weather(weather, city_name)
                parts.append(weather_text)

        fun_fact = random.choice(FUN_FACTS).format(city=city_name)
        parts.append(fun_fact)

        body = "\n\n".join(parts)

        return {
            "city": city_key,
            "city_name": city_name,
            "body": body,
            "weather_included": include_weather and self.weather_api_key is not None,
            "generated_at": datetime.utcnow(),
        }

    def get_available_cities(self) -> list[dict]:
        return [{"key": key, "name": config["name"]} for key, config in CITIES_CONFIG.items()]


city_source = CitySource()
