import asyncio
import logging
import os
from google import genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# Token loglarda ochiq chiqib ketmasligi uchun httpx INFO loglarini o'chiramiz
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN muhit o'zgaruvchisi topilmadi!")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY muhit o'zgaruvchisi topilmadi!")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Salom! Men Gemini AI ulangan botman. Savolingizni yozing."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    await update.message.chat.send_action(action="typing")

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=user_text,
        )
        reply_text = response.text or "Javob bo'sh qaytdi."

        for i in range(0, len(reply_text), 4096):
            await update.message.reply_text(reply_text[i : i + 4096])
    except Exception as e:
        logger.error("Gemini xatosi: %s", e)
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")


def main() -> None:
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .get_updates_connect_timeout(30.0)
        .get_updates_read_timeout(30.0)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi...")
    app.run_polling(
        bootstrap_retries=-1,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
    
