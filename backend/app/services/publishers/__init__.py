from app.services.publishers.telegram import telegram_publisher, TelegramPublisher
from app.services.publishers.vk import vk_publisher, VKPublisher
from app.services.publishers.wordpress import wordpress_publisher, WordPressPublisher

__all__ = [
    "telegram_publisher",
    "TelegramPublisher",
    "vk_publisher",
    "VKPublisher",
    "wordpress_publisher",
    "WordPressPublisher",
]
