from dotenv import load_dotenv
import os
import asyncio
import requests

from telethon import TelegramClient, events
from telethon.sessions import StringSession

# === ХРАНИЛИЩЕ ПРОЧИТАННЫХ ID ===
SEEN_FILE = "seen.txt"

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(map(int, f.read().splitlines()))
    except FileNotFoundError:
        return set()

def save_seen(msg_id):
    with open(SEEN_FILE, "a") as f:
        f.write(f"{msg_id}\n")

seen_messages = load_seen()

# === НАСТРОЙКИ ===
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = 1035490546

CHANNELS = [
    "mari_vakansii",
    "frilancru",
    "freelansvipchat",
    "birjafreelance",
    "frilanserov_chat",
    "biznes_voronej",
    "dsgn_vacancies",
    "freelancce",
    "frilanser_vacansii",
    "vakansi_rus",
    "FLPautinka"
]

INCLUDE = [
    "дизайн", "веб", "ui", "ux", "интерфейс", "tilda", "лендинг",
    "сайт", "веб-дизайн", "прототип", "визуал", "логотип", "брендинг", 
    "дизайнер", "веб-дизайнер", "веб-дизайн", "Сайтолог", "Сайтодел", 
    "Figma", "#ищу", "#тильда", "#сайт", "#дизайнер", "#Tilda", "#Дизайн"
]

EXCLUDE = [
    "за отзыв", "портфолио", "1000", "бесплатно",
    "#помогу", "#предлагаю", "#сделаю", "предлагаю", "помогу", "готов",
    "заберите", "если нужно", "кому нужно", "предоставляю", "научу", "проконсультирую", 
    "#Рилсмейкера", "#копирайтер", "#рилсы", "отзывы"
]

# === TELETHON ПАРСЕР ===
async def start_telethon():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()

    # Проверка подключения к каналам
    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)
            print(f"Подключен к каналу: {entity.title}")
        except Exception as e:
            print(f"Ошибка при подключении к каналу {channel}: {e}")
            continue

    @client.on(events.NewMessage(chats=CHANNELS))
    async def new_message_handler(event):
        print("📥 Поймано сообщение:")
        print(event.message.message)

        message_id = event.id
        if message_id in seen_messages:
            return
        seen_messages.add(message_id)
        save_seen(message_id)

        if event.message.message:
            text = event.message.message.lower()

            # Фильтрация по ключевым словам и исключениям
            if any(w in text for w in INCLUDE) and not any(bad in text for bad in EXCLUDE):
                print("Сообщение прошло фильтрацию!")  # Логируем успешную фильтрацию
                author = await event.get_sender()
                username = getattr(author, 'username', None)
                user_id = author.id

                msg = f"📥 Новая вакансия:\n\n{event.message.message}"

                if username:
                    reply_markup = {
                        "inline_keyboard": [[
                            {"text": "✉️ Откликнуться", "url": f"https://t.me/{username}"}
                        ]],
                    }
                else:
                    reply_markup = {
                        "inline_keyboard": [[
                            {"text": "✉️ Откликнуться", "url": f"tg://user?id={user_id}"}
                        ]],
                    }

                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": OWNER_ID,
                    "text": msg,
                    "reply_markup": reply_markup
                }
                requests.post(url, json=payload)

    print("✅ JobClear запущен: парсер с Telethon")
    await client.run_until_disconnected()

# === ЗАПУСК ВСЕГО ===
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_telethon())
    loop.run_forever()
