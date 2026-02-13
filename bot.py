"""
Главный файл Telegram бота для проверки подписки и отправки медитации
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError

import config
import messages
import keyboards


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_subscription(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """
    Проверяет подписку пользователя на канал

    Args:
        context: Контекст бота
        user_id: ID пользователя

    Returns:
        bool: True если подписан, False если нет
    """
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=config.CHANNEL_ID,
            user_id=user_id
        )

        # Статусы участников канала:
        # 'creator' - создатель
        # 'administrator' - администратор
        # 'member' - обычный участник
        # 'restricted' - ограниченный пользователь (может быть подписан)
        # 'left' - покинул канал
        # 'kicked' - был исключен

        subscribed_statuses = ['creator', 'administrator', 'member', 'restricted']
        is_subscribed = chat_member.status in subscribed_statuses

        logger.info(f"Проверка подписки пользователя {user_id}: статус = {chat_member.status}, подписан = {is_subscribed}")

        return is_subscribed

    except TelegramError as e:
        logger.error(f"Ошибка при проверке подписки пользователя {user_id}: {e}")
        return False


async def create_invite_link(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Создает одноразовую ссылку-приглашение в канал

    Args:
        context: Контекст бота

    Returns:
        str: Ссылка-приглашение
    """
    try:
        # Создаем одноразовую ссылку (член_лимит = 1)
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=config.CHANNEL_ID,
            member_limit=1,  # Одноразовая ссылка
            name=None  # Можно добавить имя для отслеживания
        )
        logger.info(f"🔗 Создана одноразовая ссылка: {invite_link.invite_link}")
        return invite_link.invite_link
    except TelegramError as e:
        logger.error(f"Ошибка при создании ссылки-приглашения: {e}")
        raise


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик аудиофайлов — выводит file_id только в консоль"""
    if update.message and update.message.audio:
        file_id = update.message.audio.file_id
        logger.info(f"🎵 Получен аудиофайл. FILE_ID: {file_id}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    logger.info(f"📩 /start от пользователя {user.id} ({user.first_name})")

    # Генерируем уникальную одноразовую ссылку для пользователя
    try:
        invite_link = await create_invite_link(context)

        # Сохраняем ссылку в user_data для использования в callback
        context.user_data['invite_link'] = invite_link

    except TelegramError as e:
        logger.error(f"Не удалось создать ссылку-приглашение: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Произошла ошибка. Попробуйте позже или свяжитесь с администратором."
        )
        return

    # Отправляем приветствие с обеими кнопками
    await context.bot.send_message(
        chat_id=chat_id,
        text=messages.WELCOME,
        parse_mode="HTML",
        reply_markup=keyboards.get_not_subscribed_keyboard(invite_link)
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    data = query.data

    logger.info(f"🔘 Callback: {data} от пользователя {user_id}")

    # Подтверждаем получение callback (убирает "часики" на кнопке)
    await query.answer()

    if data == "check_subscription":
        # Проверяем подписку
        is_subscribed = await check_subscription(context, user_id)

        if is_subscribed:
            logger.info(f"✅ Пользователь {user_id} подписан на канал")

            # Удаляем предыдущее сообщение с кнопкой проверки
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except TelegramError as e:
                logger.error(f"Не удалось удалить сообщение: {e}")

            # Отправляем кнопку для получения медитации (Сообщение 3, ветка 2)
            await context.bot.send_message(
                chat_id=chat_id,
                text=messages.SUBSCRIPTION_CONFIRMED,
                reply_markup=keyboards.get_meditation_keyboard()
            )
        else:
            logger.info(f"❌ Пользователь {user_id} не подписан на канал")

            # Получаем сохраненную ссылку или создаем новую
            invite_link = context.user_data.get('invite_link')
            if not invite_link:
                try:
                    invite_link = await create_invite_link(context)
                    context.user_data['invite_link'] = invite_link
                except TelegramError as e:
                    logger.error(f"Не удалось создать ссылку: {e}")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="⚠️ Произошла ошибка. Попробуйте позже."
                    )
                    return

            # Редактируем существующее сообщение вместо отправки нового
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=messages.NOT_SUBSCRIBED,
                    parse_mode="HTML",
                    reply_markup=keyboards.get_not_subscribed_keyboard(invite_link)
                )
            except TelegramError as e:
                logger.error(f"Не удалось отредактировать сообщение: {e}")
                # Если не удалось отредактировать, отправляем новое
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=messages.NOT_SUBSCRIBED,
                    parse_mode="HTML",
                    reply_markup=keyboards.get_not_subscribed_keyboard(invite_link)
                )

    elif data == "get_meditation":
        # Отправляем аудиопрактику
        logger.info(f"🎧 Отправка медитации пользователю {user_id}")

        try:
            # Отправляем текст с описанием
            await context.bot.send_message(
                chat_id=chat_id,
                text=messages.MEDITATION,
                parse_mode="HTML"
            )

            # Отправляем аудиофайл по file_id
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=config.AUDIO_FILE_ID,
                title="Регуляция состояния",
                performer="ASHAMAYA"
            )

            logger.info(f"✅ Медитация отправлена пользователю {user_id}")

        except Exception as e:
            logger.error(f"Ошибка при отправке аудио: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=messages.AUDIO_SEND_ERROR
            )


def main() -> None:
    """Запуск бота"""
    logger.info("🚀 Запуск бота...")

    # Создаем приложение
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота
    logger.info("✅ Бот запущен и готов к работе")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
