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
API_ID = 26437413
API_HASH = "e1afb084d8c5896f0b685eeaa1b994f7"
SESSION_STRING = "1ApWapzMBu4GyzD0LfoYv1iWp4ph3KF_rwYcMtsEYuhLfvJykAPQHBjff1ir4qI3pxjm4hoeq-NYsG2h-xI-yN6r04L_wfO-LDyu2hhlz-nsFew7bvGb7ORbtd0L_5hNyQve6S6eZkRmAImgViJGxRe3v_ASVuFwrrTVdwj0_51dK5Mk4Ji9Z3Rck2dEgUx7U8CBR3C5d6XVE7UVBHrTiFHdrRFHFaS-cC3bN0uaM67gZXSPWXSsn8_FjUuNBufQf-xSH-i-hJ5DlpySetEdxD9OMghYhN27N5NFHypbonMUgUbPLxE5dG67BYuzsIA94Tr7xUzpuiD292rUkC348d8XWLCuL3gU="
BOT_TOKEN = "7861416922:AAFlxd-_vKdcTTUqowJhcor8xi-Nla2dtI8"
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
    "сайт", "веб-дизайн", "прототип", "визуал", "логотип", "брендинг" , "дизайнер" , "веб-дизайнер" , "веб-дизайн"
    , "Сайтолог" , "Сайтодел" , "Figma" , "#ищу"
]

EXCLUDE = [
    "за отзыв", "ищу работу", "портфолио", "1000", "бесплатно",
    "#помогу", "#предлагаю", "#сделаю", "предлагаю", "помогу", "готов",
    "заберите", "пишите", "если нужно", "кому нужно", "предоставляю", "научу", "проконсультирую"
]

# === AIORAM БОТ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("👤 Личный кабинет"))

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я — JobClear.\n\n"
        "Я буду присылать тебе только адекватные вакансии по дизайну — без трэша, за отзыв и прочего мусора.",
        reply_markup=kb
    )

@dp.message_handler(text="👤 Личный кабинет")
async def profile(message: types.Message):
    await message.answer("🧾 Подписка: неограниченный доступ\n🎯 Категория: Дизайн\n")

# === TELETHON ПАРСЕР ===
async def start_telethon():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()

    @client.on(events.NewMessage(chats=CHANNELS))
    async def new_message_handler(event):
        message_id = event.id
        if message_id in seen_messages:
            return
        seen_messages.add(message_id)
        save_seen(message_id)

        if event.message.message:
            text = event.message.message.lower()

            if any(w in text for w in INCLUDE) and not any(bad in text for bad in EXCLUDE):
                author = await event.get_sender()
                username = getattr(author, 'username', None)
                user_id = author.id

                msg = f"📥 Новая вакансия:\n\n{event.message.message}"

                if username:
                    reply_markup = {
                        "inline_keyboard": [[
                            {"text": "✉️ Откликнуться", "url": f"https://t.me/{username}"}
                        ]]
                    }
                else:
                    reply_markup = {
                        "inline_keyboard": [[
                            {"text": "✉️ Откликнуться", "url": f"tg://user?id={user_id}"}
                        ]]
                    }

                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": OWNER_ID,
                    "text": msg,
                    "reply_markup": reply_markup
                }
                requests.post(url, json=payload)

    print("✅ JobClear запущен: бот + парсер")
    await client.run_until_disconnected()

# === ЗАПУСК ВСЕГО ===
if __name__ == '__main__':
    from admin import register_admin
    register_admin(dp)

    loop = asyncio.get_event_loop()
    loop.create_task(start_telethon())
    executor.start_polling(dp, skip_updates=True)
