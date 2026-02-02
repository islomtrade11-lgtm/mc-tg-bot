import asyncio
import subprocess
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

# ================== ENV & SECURITY ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS_RAW = os.getenv("OWNER_IDS")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not OWNER_IDS_RAW:
    raise RuntimeError("OWNER_IDS is not set")

ALLOWED_USERS = {int(x.strip()) for x in OWNER_IDS_RAW.split(",") if x.strip()}

# ================== BOT INIT ==================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

mc_process = None
ai_enabled = False

# ================== UI ==================

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ Start", callback_data="start"),
            InlineKeyboardButton(text="⏹ Stop", callback_data="stop")
        ],
        [
            InlineKeyboardButton(text="💬 Say", callback_data="say"),
            InlineKeyboardButton(text="🧠 AI ON / OFF", callback_data="ai")
        ],
        [
            InlineKeyboardButton(text="📊 Status", callback_data="status")
        ]
    ])

def status_text():
    return (
        "🤖 Minecraft Bot Control\n\n"
        f"🟢 Status: {'ONLINE' if mc_process else 'OFFLINE'}\n"
        f"🧠 AI: {'ON' if ai_enabled else 'OFF'}"
    )

# ================== HELPERS ==================

def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS

# ================== HANDLERS ==================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if not is_allowed(message.from_user.id):
        return

    await message.answer(
        status_text(),
        reply_markup=main_keyboard()
    )

@dp.callback_query()
async def on_callback(call: types.CallbackQuery):
    global mc_process, ai_enabled

    if not is_allowed(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    data = call.data

    if data == "start":
        if mc_process is None:
            mc_process = subprocess.Popen(["node", "mc.js"])
            await call.message.answer("🟢 Minecraft бот запущен")
        else:
            await call.message.answer("⚠️ Бот уже запущен")

    elif data == "stop":
        if mc_process:
            mc_process.kill()
            mc_process = None
            await call.message.answer("🔴 Minecraft бот остановлен")
        else:
            await call.message.answer("⚠️ Бот не запущен")

    elif data == "ai":
        ai_enabled = not ai_enabled
        os.environ["AI_ENABLED"] = "1" if ai_enabled else "0"
        await call.message.answer(f"🧠 AI {'включён' if ai_enabled else 'выключен'}")

    elif data == "say":
        await call.message.answer("✍️ Напиши сообщение для Minecraft чата")
        dp.message.register(wait_say_message)

    elif data == "status":
        await call.message.answer(
            status_text(),
            reply_markup=main_keyboard()
        )

    await call.answer()

# ================== SAY MODE ==================

async def wait_say_message(message: types.Message):
    if not is_allowed(message.from_user.id):
        return

    with open("say.txt", "w", encoding="utf-8") as f:
        f.write(message.text)

    await message.answer("✅ Сообщение отправлено в Minecraft")
    dp.message.unregister(wait_say_message)

# ================== MAIN ==================

async def main():
    print("🤖 Telegram bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
