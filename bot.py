from dotenv import load_dotenv
load_dotenv()
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import requests
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

COBALT_API_URL = "https://api.cobalt.tools/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Отправь мне ссылку на видео или аудио, и я дам ссылку для скачивания!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Просто отправь ссылку, например, на YouTube или TikTok."
    )

async def download_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("Пожалуйста, отправь правильную ссылку!")
        return

    try:
        headers = {"Accept": "application/json"}
        payload = {"url": url}
        response = requests.post(COBALT_API_URL, json=payload, headers=headers)

        if response.status_code != 200:
            await update.message.reply_text("Ошибка. Попробуй другую ссылку!")
            return

        data = response.json()
        if data.get("status") == "error":
            await update.message.reply_text(f"Ошибка: {data.get('text', 'Неизвестная ошибка')}")
        elif data.get("status") == "redirect":
            await update.message.reply_text(f"Скачать: {data.get('url')}")
        elif data.get("status") == "picker":
            picker = data.get("picker", [])
            if picker:
                reply = "Выбери вариант:\n"
                for item in picker:
                    reply += f"- {item.get('url', 'Нет ссылки')}\n"
                await update.message.reply_text(reply)
            else:
                await update.message.reply_text("Варианты не найдены.")
        else:
            await update.message.reply_text("Что-то пошло не так.")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Ошибка. Попробуй позже!")

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Токен бота не найден!")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_content))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()