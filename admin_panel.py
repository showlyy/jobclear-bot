import json
from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import Dispatcher

SUBS_FILE = "subscribers.json"
OWNER_ID = 1035490546  # твой Telegram ID

def load_subs():
    try:
        with open(SUBS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_subs(data):
    with open(SUBS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(user_id):
    return user_id == OWNER_ID

def register_admin(dp: Dispatcher):
    @dp.message_handler(commands=["выдать"])
    async def cmd_grant(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        args = message.text.split()
        if len(args) != 3:
            await message.reply("Формат: /выдать @username 30")
            return
        username_or_phone, days_str = args[1], args[2]
        try:
            days = int(days_str)
        except:
            await message.reply("Укажи число дней.")
            return

        subs = load_subs()
        key = username_or_phone.lower()
        until = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")
        subs[key] = {"until": until}
        save_subs(subs)
        await message.reply(f"✅ Подписка для {username_or_phone} до {until}")

    @dp.message_handler(commands=["удалить"])
    async def cmd_remove(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        args = message.text.split()
        if len(args) != 2:
            await message.reply("Формат: /удалить @username")
            return
        key = args[1].lower()
        subs = load_subs()
        if key in subs:
            del subs[key]
            save_subs(subs)
            await message.reply(f"❌ Подписка у {key} удалена")
        else:
            await message.reply("Такой подписки нет.")

    @dp.message_handler(commands=["подписчики"])
    async def cmd_list(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        subs = load_subs()
        if not subs:
            await message.reply("Нет подписчиков.")
            return
        text = "\n".join([f"{k}: до {v['until']}" for k, v in subs.items()])
        await message.reply(f"📋 Подписчики:\n{text}")
