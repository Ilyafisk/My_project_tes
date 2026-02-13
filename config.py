import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
AUDIO_FILE_ID = "CQACAgQAAxkBAAIrF2mPcAmYYiq3aJ9v6SsqeXcplH9aAAJ_GgACgNthUAcD7pqFNXHTOgQ"

# Проверка обязательных переменных окружения
if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN не установлен в .env файле')

if not CHANNEL_ID:
    raise ValueError('CHANNEL_ID не установлен в .env файле')
