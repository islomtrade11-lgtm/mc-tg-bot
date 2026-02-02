import asyncio
import subprocess
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

mc_process = None
ai_enabled = False


def keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Start", callback_data="start"),
         InlineKeyboardButton(text="⏹ Stop", callback_data="stop")],
        [InlineKeyboardButton(text="💬 Say", callback_data="say")],
        [InlineKeyboardButton(text="🧠 AI ON/OFF", callback_data="ai")],
        [InlineKeyboardButton(text="📊 Status", callback_data="status")]
    ])


@dp.message(CommandStart())
async def start(msg: types.Message):
    if msg.from_user.id != OWNER_ID:
        return
    await msg.answer("🤖 Minecraft Bot Control", reply_markup=keyboard())


@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    global mc_process, ai_enabled

    if call.from_user.id != OWNER_ID:
        return

    if call.data == "start":
        if mc_process is None:
            mc_process = subprocess.Popen(["node", "mc.js"])
            await call.message.answer("🟢 Minecraft bot started")
        else:
            await call.message.answer("⚠️ Already running")

    elif call.data == "stop":
        if mc_process:
            mc_process.kill()
            mc_process = None
            await call.message.answer("🔴 Minecraft bot stopped")
        else:
            await call.message.answer("⚠️ Not running")

    elif call.data == "ai":
        ai_enabled = not ai_enabled
        os.environ["AI_ENABLED"] = "1" if ai_enabled else "0"
        await call.message.answer(f"🧠 AI {'ON' if ai_enabled else 'OFF'}")

    elif call.data == "say":
        await call.message.answer("✍️ Напиши сообщение в чат MC")
        dp.message.register(wait_message)

    elif call.data == "status":
        await call.message.answer(
            f"Status: {'ONLINE' if mc_process else 'OFFLINE'}\nAI: {'ON' if ai_enabled else 'OFF'}"
        )


async def wait_message(msg: types.Message):
    if msg.from_user.id != OWNER_ID:
        return
    with open("say.txt", "w", encoding="utf-8") as f:
        f.write(msg.text)
    await msg.answer("✅ Отправлено в Minecraft")
    dp.message.unregister(wait_message)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
