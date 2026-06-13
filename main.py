import asyncio
import aiohttp
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")

LOG_CHANNEL = "@ainazorat"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ================= LOG =================
async def send_log(text: str):
    try:
        await bot.send_message(chat_id=LOG_CHANNEL, text=text)
    except Exception as e:
        print("LOG ERROR:", e)


# ================= BUTTON =================
def retry_button(task_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔁 Yana qo‘shish",
                callback_data=f"retry:{task_id}"
            )
        ]
    ])


# ================= START =================
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Ariza raqamini yuboring 👇")


# ================= MAIN HANDLER =================
@dp.message(F.text)
async def sync_handler(message: Message):
    task_id = message.text.strip()

    url = f"{BASE_URL}&task_id={task_id}"

    headers = {
        "Authorization": f"Token {ACCESS_TOKEN}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                response_text = await response.text()

                # ================= SUCCESS =================
                if 200 <= response.status < 300:
                    await message.answer(
                        "Successful ✅",
                        reply_markup=retry_button(task_id)
                    )

                    await send_log(
                        f"SUCCESS ✅\n"
                        f"User: {message.from_user.id}\n"
                        f"Task ID: {task_id}\n"
                        f"Status: {response.status}"
                    )

                # ================= ARIZA XATO (400) =================
                elif response.status == 400:
                    await message.answer(
                        "❌ Ariza raqami xato yoki topilmadi",
                        reply_markup=retry_button(task_id)
                    )

                    await send_log(
                        f"INVALID ARIZA ❌\n"
                        f"User: {message.from_user.id}\n"
                        f"Task ID: {task_id}\n"
                        f"Status: 400\n"
                        f"Response: {response_text[:200]}"
                    )

                # ================= OTHER ERRORS =================
                else:
                    await message.answer(
                        f"❌ Xatolik: {response.status}",
                        reply_markup=retry_button(task_id)
                    )

                    await send_log(
                        f"FAILED ❌\n"
                        f"User: {message.from_user.id}\n"
                        f"Task ID: {task_id}\n"
                        f"Status: {response.status}\n"
                        f"Response: {response_text[:200]}"
                    )

    except Exception as e:
        await message.answer(
            f"Server error ❌\n{str(e)}",
            reply_markup=retry_button(task_id)
        )

        await send_log(
            f"ERROR 🔥\n"
            f"User: {message.from_user.id}\n"
            f"Task ID: {task_id}\n"
            f"Error: {str(e)}"
        )


# ================= CALLBACK =================
@dp.callback_query(F.data.startswith("retry:"))
async def retry_handler(callback: CallbackQuery):
    task_id = callback.data.split(":")[1]

    await callback.message.answer("Yangi ariza raqamini yuboring 👇")
    await callback.answer()


# ================= START BOT =================
async def main():
    print("Bot ishga tushdi...")
    await send_log("🟢 Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())