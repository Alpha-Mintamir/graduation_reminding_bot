import os
import datetime
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the Telegram token from environment variable
TELEGRAM_TOKEN = '8171453958:AAH4-RbH7spozWrcjVgtGb1rF_EFNzfnnyM'

# Graduation date
GRADUATION_DATE = datetime.date(2025, 7, 5)

def create_progress_image(days_left: int, total_days: int) -> BytesIO:
    """
    Create a simple progress bar image showing the days remaining.
    """
    logger.info("Creating progress image with %d days left out of %d total days", days_left, total_days)
    width, height = 300, 100
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # Calculate progress (completed fraction)
    progress = (total_days - days_left) / total_days if total_days else 0
    bar_width = int(width * progress)
    draw.rectangle([0, 30, bar_width, 70], fill="green")

    # Add text to the image
    font = ImageFont.load_default()
    text = f"{days_left} days left!"
    
    # Use textbbox to calculate the text size
    text_bbox = draw.textbbox((0, 0), text, font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    draw.text(
        ((width - text_width) / 2, (height - text_height) / 2),
        text,
        font=font,
        fill="black",
    )

    # Save image to a BytesIO stream
    byte_io = BytesIO()
    image.save(byte_io, "PNG")
    byte_io.seek(0)
    logger.info("Progress image created successfully")
    return byte_io
    """
    Create a simple progress bar image showing the days remaining.
    """
    logger.info("Creating progress image with %d days left out of %d total days", days_left, total_days)
    width, height = 300, 100
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # Calculate progress (completed fraction)
    progress = (total_days - days_left) / total_days if total_days else 0
    bar_width = int(width * progress)
    draw.rectangle([0, 30, bar_width, 70], fill="green")

    # Add text to the image
    font = ImageFont.load_default()
    text = f"{days_left} days left!"
    text_width, text_height = draw.textsize(text, font)
    draw.text(
        ((width - text_width) / 2, (height - text_height) / 2),
        text,
        font=font,
        fill="black",
    )

    # Save image to a BytesIO stream
    byte_io = BytesIO()
    image.save(byte_io, "PNG")
    byte_io.seek(0)
    logger.info("Progress image created successfully")
    return byte_io

async def send_graduation_message(context: CallbackContext) -> None:
    """
    Calculates days remaining, creates an image with progress,
    and sends it to the target chat.
    """
    logger.info("Executing send_graduation_message job")
    today = datetime.date.today()
    days_left = (GRADUATION_DATE - today).days
    logger.info("Today's date is %s; Days left until graduation: %d", today, days_left)

    # For progress calculation, we define a total period.
    total_days = (GRADUATION_DATE - datetime.date(2025, 1, 1)).days
    logger.info("Total days (from Jan 1, 2025 to graduation): %d", total_days)

    if days_left >= 0:
        progress_image = create_progress_image(days_left, total_days)
        chat_id = context.job.data  # the job's data holds the chat_id
        logger.info("Sending graduation message to chat_id %s", chat_id)
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=progress_image,
            caption=f"Hey guys, don't forget that you are left with {days_left} days for graduation!",
        )
    else:
        logger.info("Graduation passed. No message will be sent.")

# In the start function, update the interval to 172800 seconds (2 days)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Starts the bot, schedules the repeating graduation countdown message,
    and sends an initial confirmation message.
    """
    chat_id = update.effective_chat.id
    logger.info("Received /start command from chat_id %s", chat_id)

    # Schedule the send_graduation_message job every 2 days (172800 seconds)
    context.job_queue.run_repeating(
        send_graduation_message, interval=172800, first=0, data=chat_id
    )
    logger.info("Scheduled send_graduation_message job for chat_id %s", chat_id)

    await update.message.reply_text(
        "Hey! I’ll keep you updated on how many days are left for graduation!"
    )
    logger.info("Sent confirmation message to chat_id %s", chat_id)

def main() -> None:
    logger.info("Starting the Telegram bot")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add command handler for the /start command
    application.add_handler(CommandHandler("start", start))
    logger.info("Added /start command handler")

    # Start polling for updates from Telegram
    logger.info("Bot is polling for updates...")
    application.run_polling()

if __name__ == "__main__":
    main()
