import json

import telebot

import logging
import sys
import os

from dashgram import Dashgram, HandlerType

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN, use_class_middlewares=True)

sdk = Dashgram(project_id=os.getenv("PROJECT_ID"), access_key=os.getenv("ACCESS_KEY"),
               api_url="http://localhost:5023/api/v1")
sdk.bind_telebot(bot)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot.polling()
