"""
Клавиатуры с инлайн-кнопками
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_not_subscribed_keyboard():
    """Клавиатура с кнопками подписки и проверки (для неподписанных)"""
    from config import CHANNEL_LINK
    keyboard = [
        [InlineKeyboardButton("👉 Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton("👉 Проверить подписку", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_meditation_keyboard():
    """Клавиатура с кнопкой получения медитации"""
    keyboard = [
        [InlineKeyboardButton("👉 Получить медитацию", callback_data="get_meditation")]
    ]
    return InlineKeyboardMarkup(keyboard)
