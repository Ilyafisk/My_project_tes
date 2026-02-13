"""
Клавиатуры с инлайн-кнопками
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_not_subscribed_keyboard(invite_link: str):
    """
    Клавиатура с обеими кнопками друг под другом (для неподписанных)

    Args:
        invite_link: Уникальная ссылка-приглашение для пользователя
    """
    keyboard = [
        [InlineKeyboardButton("👉 Подписаться на закрытый канал", url=invite_link)],
        [InlineKeyboardButton("👉 Проверить подписку", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_meditation_keyboard():
    """Клавиатура с кнопкой получения медитации"""
    keyboard = [
        [InlineKeyboardButton("👉 Получить медитацию", callback_data="get_meditation")]
    ]
    return InlineKeyboardMarkup(keyboard)
