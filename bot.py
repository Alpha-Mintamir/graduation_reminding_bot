import os
import datetime
import time
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from io import BytesIO


# Replace with your own Telegram bot token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Graduation date
GRADUATION_DATE = datetime.date(2025, 7, 5)

# Create the progress image
def create_progress_image(days_left, total_days):
    # Create a blank image
    width, height = 300, 100
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Draw a progress bar
    progress = (total_days - days_left) / total_days
    bar_width = int(width * progress)
    draw.rectangle([0, 30, bar_width, 70], fill='green')

    # Add text
    font = ImageFont.load_default()
    text = f"{days_left} days left!"
    text_width, text_height = draw.textsize(text, font)
    draw.text(((width - text_width) / 2, (height - text_height) / 2), text, font=font, fill='black')

    # Save the image to a BytesIO object
    byte_io = BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io


# Function to calculate days left and send message
def send_graduation_message(context: CallbackContext):
    today = datetime.date.today()
    days_left = (GRADUATION_DATE - today).days
    total_days = (GRADUATION_DATE - datetime.date(2025, 1, 1)).days  # Total days in the year
    if days_left >= 0:
        # Create the image
        progress_image = create_progress_image(days_left, total_days)

        # Send the message to the group
        context.bot.send_photo(
            chat_id=context.job.context,
            photo=progress_image,
            caption=f"Hey guys, don't forget that you are left with {days_left} days for graduation!"
        )


# Command to start the bot and set up periodic messages
def start(update: Update, context: CallbackContext):
    # Start the scheduled task to send messages every two days
    chat_id = update.message.chat_id
    context.job_queue.run_repeating(send_graduation_message, interval=172800, first=0, context=chat_id)
    update.message.reply_text("Hey! I’ll keep you updated on how many days are left for graduation!")


def main():
    # Set up the updater and dispatcher
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))

    # Set up the scheduler to run in the background
    scheduler = BackgroundScheduler()
    scheduler.start()

    # Start the bot
    updater.start_polling()

    # Run the bot until you stop it
    updater.idle()


if __name__ == '__main__':
    main()
