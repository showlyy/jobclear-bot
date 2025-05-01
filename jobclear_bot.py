from dotenv import load_dotenv
import os
import asyncio
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from telethon import TelegramClient, events
from telethon.sessions import StringSession

# === ХРАНИЛИЩЕ ПРОЧИТАННЫХ ID ===
SEEN_FILE = "seen.txt"

def load_seen():
    print("🔍 Загружаем файл с сохранёнными ID...")
    try:
        with open(SEEN_FILE, "r") as f:
            seen = set(map(int, f.read().splitlines()))
            print(f"✅ Загружено {len(seen)} сохранённых ID.")
            return seen
    except FileNotFoundError:
        print("❗️ Файл с ID не найден. Создадим новый.")
        return set()

def save_seen(msg_id):
    print(f"💾 Сохраняем ID сообщения: {msg_id}")
    with open(SEEN_FILE, "a") as f:
        f.write(f"{msg_id}\n")

seen_messages = load_seen()

# === НАСТРОЙКИ ===
load_dotenv()

# Используем переменные окружения
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
    "Figma", "#ищу", "#тильда", "#сайт", "#дизайнер", "#Tilda", "#Дизайн", "#лендинг", "лендинг", "вебинар"
]

EXCLUDE = [
    "за отзыв", "портфолио", "1000", "бесплатно",
    "#помогу", "#предлагаю", "#сделаю", "предлагаю", "помогу", "готов",
    "заберите", "если нужно", "кому нужно", "предоставляю", "научу", "проконсультирую", 
    "#Рилсмейкера", "#копирайтер", "#рилсы", "отзывы", "18 лет", "помощник", "хостинг", "18 ле"
    , "18", "Озон"
]

# === AIORAM БОТ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("👤 Личный кабинет"))

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    print(f"🟢 Получена команда /start от {message.from_user.first_name}")
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я — JobClear.\n\n"
        "Я буду присылать тебе только адекватные вакансии по дизайну — без трэша, за отзыв и прочего мусора.",
        reply_markup=kb
    )

@dp.message_handler(text="👤 Личный кабинет")
async def profile(message: types.Message):
    print(f"🟢 Получена команда 'Личный кабинет' от {message.from_user.first_name}")
    await message.answer("🧾 Подписка: неограниченный доступ\n🎯 Категория: Дизайн\n")

# === TELETHON ПАРСЕР ===
async def start_telethon():
    print("🔌 Подключение к Telegram...")
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    print("✅ Подключение успешно.")

    @client.on(events.NewMessage(chats=CHANNELS))
    async def new_message_handler(event):
        print("📥 Поймано сообщение:")
        print(event.message.message)  # Логируем текст сообщения

        message_id = event.id
        print(f"Получен message_id: {message_id}")

        if message_id in seen_messages:
            print(f"Сообщение {message_id} уже обработано.")
            return
        seen_messages.add(message_id)
        save_seen(message_id)

        if event.message.message:
            text = event.message.message.lower()
            print(f"Текст сообщения: {text}")

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

                print(f"Отправка сообщения пользователю {OWNER_ID}")
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": OWNER_ID,
                    "text": msg,
                    "reply_markup": reply_markup
                }
                response = requests.post(url, json=payload)
                print(f"Ответ от Telegram API: {response.status_code} {response.text}")

    print("✅ JobClear запущен: бот + парсер")
    await client.run_until_disconnected()

# === ЗАПУСК ВСЕГО ===
if __name__ == '__main__':
    print("🔄 Регистрация администратора...")
    from admin_panel import register_admin
    register_admin(dp)

    loop = asyncio.get_event_loop()
    loop.create_task(start_telethon())

    # Удалена строка с app.run, так как она не нужна для long-polling
    print("🚀 Запуск бота через long polling...")
    executor.start_polling(dp, skip_updates=True)
