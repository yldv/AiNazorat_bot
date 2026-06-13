import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
import os
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

BASE_URL = os.getenv("BASE_URL")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Task ID yuboring.")


@dp.message(F.text)
async def sync_handler(message: Message):
    task_id = message.text.strip()

    url = f"{BASE_URL}&task_id={task_id}"

    headers = {
        "Authorization": f"Token {ACCESS_TOKEN}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers
            ) as response:

                response_text = await response.text()

                if response.status == 200:
                    await message.answer("Successful ✅")
                else:
                    await message.answer(
                        f"Failed ❌\n"
                        f"Status: {response.status}\n"
                        f"Response: {response_text[:500]}"
                    )

    except Exception as e:
        await message.answer(
            f"Server error ❌\n{str(e)}"
        )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())