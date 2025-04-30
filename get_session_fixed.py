from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Используем новый api_id и api_hash
api_id = 26437413  # Здесь оставь без изменений
api_hash = "e1afb084d8c5896f0b685eeaa1b994f7"  # Новый api_hash от твоего бота

# Создание клиента для генерации сессии
client = TelegramClient(
    StringSession(),
    api_id,
    api_hash,
    device_model="Windows PC",  # Маскировка устройства
    system_version="10.0",  # Маскировка системы
    app_version="9.4",  # Версия приложения
    lang_code="en",  # Язык
    system_lang_code="en"
)

# Генерация сессии
with client:
    print("Войдите в Telegram...")
    session = client.session.save()
    print("✅ Session string:")
    print(session)