import os
import datetime
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from pytz import timezone
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    JobQueue,
)

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GRADUATION_DATE = datetime.date(2025, 7, 5)
TIMEZONE = timezone("UTC")  # Change to your desired timezone

def create_progress_image(days_left: int, total_days: int) -> BytesIO:
    logger.info("Creating progress image with %d days left out of %d total days", days_left, total_days)
    width, height = 300, 100
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    progress = (total_days - days_left) / total_days if total_days else 0
    bar_width = int(width * progress)
    draw.rectangle([0, 30, bar_width, 70], fill="green")

    font = ImageFont.load_default()
    text = f"{days_left} days left!"
    text_bbox = draw.textbbox((0, 0), text, font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    draw.text(
        ((width - text_width) / 2, (height - text_height) / 2),
        text,
        font=font,
        fill="black",
    )

    byte_io = BytesIO()
    image.save(byte_io, "PNG")
    byte_io.seek(0)
    return byte_io

async def send_graduation_message(context: CallbackContext) -> None:
    logger.info("Executing send_graduation_message job")
    today = datetime.date.today()
    days_left = (GRADUATION_DATE - today).days
    total_days = (GRADUATION_DATE - datetime.date(2025, 1, 1)).days

    if days_left >= 0:
        progress_image = create_progress_image(days_left, total_days)
        chat_id = context.job.data
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=progress_image,
            caption=f"Hey guys, {days_left} days left for graduation!",
        )
    else:
        logger.info("Graduation passed.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    context.job_queue.run_repeating(
        send_graduation_message, interval=172800, first=0, data=chat_id
    )
    await update.message.reply_text("I’ll update you every 2 days on graduation!")

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).job_queue(
        job_queue=JobQueue(timezone=TIMEZONE)
    ).build()
    
    application.add_handler(CommandHandler("start", start))
    
    application.run_webhook(
        listen='0.0.0.0',
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}",
        secret_token=SECRET_TOKEN  # Optional security measure
    )

if __name__ == "__main__":
    main()
