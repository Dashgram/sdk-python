import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from dashgram import Dashgram, HandlerType


TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

sdk = Dashgram(project_id=getenv("PROJECT_ID"), access_key=getenv("ACCESS_KEY"),
               api_url="http://localhost:5023/api/v1")
# sdk.bind_aiogram(dp)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await sdk.track_event(message, handler_type=HandlerType.MESSAGE)

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message, event_update) -> None:
    await sdk.track_event(event_update)

    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())