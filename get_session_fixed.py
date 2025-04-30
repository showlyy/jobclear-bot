from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 26437413
api_hash = "e1afb084d8c5896f0b685eeaa1b994f7"

client = TelegramClient(
    StringSession(),
    api_id,
    api_hash,
    device_model="Windows PC",
    system_version="10.0",
    app_version="9.4",
    lang_code="en",
    system_lang_code="en"
)

with client:
    print("Войдите в Telegram...")
    session = client.session.save()
    print("✅ Session string:")
    print(session)