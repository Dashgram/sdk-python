import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from dashgram import Dashgram

import sys
import os

sdk = Dashgram(project_id=os.getenv("PROJECT_ID"), access_key=os.getenv("ACCESS_KEY"),
               api_url="http://localhost:5023/api/v1")

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await sdk.track_event(update)

    await update.message.reply_text(update.message.text)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    sdk.bind_telegram(application)

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    main()