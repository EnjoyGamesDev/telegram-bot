import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, this is my first Telegram bot.")
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/video - Sends a sample video")
    
async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_video(video="example_videos/example_1.mp4")
    
    
def main():
    # Create the application
    print("Starting the bot")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Start the commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("video", video_command))
    
    print("Polling...")
    app.run_polling()
    


if __name__ == "__main__":
    main()