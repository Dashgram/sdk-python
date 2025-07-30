import json

from telebot.async_telebot import AsyncTeleBot

import logging
import asyncio
import sys
import os

from dashgram import Dashgram, HandlerType

TOKEN = os.getenv("BOT_TOKEN")

bot = AsyncTeleBot(TOKEN)

sdk = Dashgram(project_id=os.getenv("PROJECT_ID"), access_key=os.getenv("ACCESS_KEY"),
               api_url="http://localhost:5023/api/v1")
sdk.bind_telebot(bot)


@bot.message_handler(func=lambda message: True)
async def handle_all_messages(message):
    await bot.send_message(message.chat.id, message.text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(bot.polling())
