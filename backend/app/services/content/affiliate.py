from typing import Optional
from datetime import datetime
import random

from app.services.ai import ai_service


class AffiliateSource:
    POST_TEMPLATES = [
        """🔥 **{product_name}**

{description}

{call_to_action}
👉 {link}""",
        """✨ Рекомендация дня!

**{product_name}**

{description}

{call_to_action}
🔗 {link}""",
        """💎 То, что вы искали:

**{product_name}**

{description}

{call_to_action}
📌 {link}""",
    ]

    CALL_TO_ACTIONS = [
        "Подробнее можно узнать здесь:",
        "Все подробности по ссылке:",
        "Узнать больше:",
        "Подробная информация:",
        "Смотреть:",
    ]

    def __init__(self):
        self.products: list[dict] = []

    def add_product(
        self,
        name: str,
        description: str,
        ref_url: str,
        category: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        price: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> dict:
        product = {
            "name": name,
            "description": description,
            "ref_url": ref_url,
            "category": category,
            "keywords": keywords or [],
            "price": price,
            "image_url": image_url,
        }
        self.products.append(product)
        return product

    def get_random_product(self) -> Optional[dict]:
        if not self.products:
            return None
        return random.choice(self.products)

    def get_products_by_category(self, category: str) -> list[dict]:
        return [p for p in self.products if p.get("category") == category]

    async def generate_post(
        self,
        product: Optional[dict] = None,
        use_ai: bool = True,
        template_style: str = "native",
    ) -> Optional[dict]:
        if product is None:
            product = self.get_random_product()

        if not product:
            return None

        if use_ai:
            ai_post = await ai_service.generate_affiliate_post(
                product_name=product["name"],
                description=product["description"],
                keywords=product.get("keywords", []),
            )

            if ai_post:
                body = f"{ai_post}\n\n👉 {product['ref_url']}"
            else:
                body = self._generate_template_post(product)
        else:
            body = self._generate_template_post(product)

        return {
            "product_name": product["name"],
            "product_category": product.get("category"),
            "body": body,
            "ref_url": product["ref_url"],
            "image_url": product.get("image_url"),
            "generated_with_ai": use_ai,
            "generated_at": datetime.utcnow(),
        }

    def _generate_template_post(self, product: dict) -> str:
        template = random.choice(self.POST_TEMPLATES)
        call_to_action = random.choice(self.CALL_TO_ACTIONS)

        description = product["description"]
        if product.get("price"):
            description += f"\n💰 Цена: {product['price']}"

        return template.format(
            product_name=product["name"],
            description=description,
            call_to_action=call_to_action,
            link=product["ref_url"],
        )

    async def generate_category_posts(
        self,
        category: str,
        count: int = 3,
        use_ai: bool = True,
    ) -> list[dict]:
        products = self.get_products_by_category(category)
        products = products[:count]

        posts = []
        for product in products:
            post = await self.generate_post(product, use_ai)
            if post:
                posts.append(post)

        return posts

    def create_short_url_placeholder(self, ref_url: str, campaign: str = "autoposting") -> str:
        return f"{ref_url}?utm_source={campaign}"


affiliate_source = AffiliateSource()
