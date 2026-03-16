import random
from typing import Optional
from datetime import datetime

from app.services.ai import ai_service


ANIMALS_DATA = [
    {
        "name": "кошка",
        "facts": [
            "Кошки могут издавать более 100 различных звуков",
            "Кошки спят 70% своей жизни",
            "У кошек более 20 вокализаций, включая мурлыканье",
        ],
    },
    {
        "name": "собака",
        "facts": [
            "У собак обоняние в 10000-100000 раз сильнее чем у людей",
            "Собаки могут понимать до 250 слов и жестов",
            "Нос каждой собаки уникален, как отпечаток пальца",
        ],
    },
    {
        "name": "дельфин",
        "facts": [
            "Дельфины спят с одним открытым глазом",
            "Дельфины узнают себя в зеркале",
            "Дельфины могут удерживать дыхание до 15 минут",
        ],
    },
    {
        "name": "слон",
        "facts": [
            "Слоны — единственные животные, которые не могут прыгать",
            "Слоны могут распознавать себя в зеркале",
            "Беременность слона длится 22 месяца",
        ],
    },
    {
        "name": "осьминог",
        "facts": [
            "У осьминога три сердца и голубая кровь",
            "Осьминоги могут менять цвет за 0.3 секунды",
            "Осьминоги умеют открывать банки и решать головоломки",
        ],
    },
    {
        "name": "медведь",
        "facts": [
            "Медведи могут бегать со скоростью до 50 км/ч",
            "У медведей отличная память на места с едой",
            "Медведи — отличные пловцы и могут проплыть много километров",
        ],
    },
    {
        "name": "пингвин",
        "facts": [
            "Пингвины могут задерживать дыхание на 20 минут",
            "Пингвины propose подарком — идеально гладким камешком",
            "Императорские пингвины могут нырять на глубину 500 метров",
        ],
    },
    {
        "name": "жираф",
        "facts": [
            "Язык жирафа может быть длиной до 50 см и имеет тёмный цвет",
            "Жирафы спят всего 30 минут в сутки",
            "У жирафов такое же количество шейных позвонков, как у людей — 7",
        ],
    },
    {
        "name": "бобр",
        "facts": [
            "Зубы бобров никогда не перестают расти",
            "Бобры строят плотины длиной до 500 метров",
            "Бобры могут оставаться под водой до 15 минут",
        ],
    },
    {
        "name": "колибри",
        "facts": [
            "Колибри — единственные птицы, которые могут летать назад",
            "Сердце колибри бьётся до 1200 раз в минуту",
            "Колибри могут взмахивать крыльями до 80 раз в секунду",
        ],
    },
]


class AnimalFactsSource:
    def __init__(self):
        self.used_facts: set[tuple[str, str]] = set()

    def get_random_animal(self) -> dict:
        return random.choice(ANIMALS_DATA)

    def get_unused_fact(self, animal_name: str) -> Optional[str]:
        animal = next((a for a in ANIMALS_DATA if a["name"] == animal_name), None)
        if not animal:
            return None

        for fact in animal["facts"]:
            key = (animal_name, fact)
            if key not in self.used_facts:
                self.used_facts.add(key)
                return fact

        return random.choice(animal["facts"])

    async def generate_fact(
        self,
        animal_name: Optional[str] = None,
        use_ai: bool = True,
    ) -> dict:
        if animal_name:
            animal = next((a for a in ANIMALS_DATA if a["name"] == animal_name), None)
            if not animal:
                animal = self.get_random_animal()
        else:
            animal = self.get_random_animal()

        base_fact = self.get_unused_fact(animal["name"])

        if use_ai:
            ai_fact = await ai_service.generate_animal_fact(animal["name"])
            if ai_fact:
                body = f"🦁 **Интересный факт о {animal['name']}**\n\n{ai_fact}"
            else:
                body = f"🦁 **Интересный факт о {animal['name']}**\n\n{base_fact}"
        else:
            body = f"🦁 **Интересный факт о {animal['name']}**\n\n{base_fact}"

        return {
            "animal": animal["name"],
            "body": body,
            "original_fact": base_fact,
            "generated_with_ai": use_ai,
            "generated_at": datetime.utcnow(),
        }

    async def generate_multiple(self, count: int = 3, use_ai: bool = True) -> list[dict]:
        facts = []
        animals = random.sample(ANIMALS_DATA, min(count, len(ANIMALS_DATA)))

        for animal in animals:
            fact = await self.generate_fact(animal["name"], use_ai)
            facts.append(fact)

        return facts


animal_facts_source = AnimalFactsSource()
