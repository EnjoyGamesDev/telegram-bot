import os, re, logging
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, VIDEO_HELP

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Regex for basic YouTube URL validation
YOUTUBE_URL_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/')

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, this is my first Telegram bot.")
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/help - See all commands\n", 
                                    VIDEO_HELP)
    
async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ You need to provide a YouTube link.\nExample: " + VIDEO_HELP)
        return

    url = context.args[0]

    if not YOUTUBE_URL_REGEX.match(url):
        await update.message.reply_text("❌ That doesn't look like a valid YouTube link.")
        return

    # Check video size before download
    is_valid, size_mb = check_video_size(url)

    if not is_valid:
        await update.message.reply_text(f"⚠️ Video is too large to send. It is {size_mb:.2f} MB (limit is 50 MB).")
        return

    await update.message.reply_text("⏳ Downloading video...")

    video_path = download_video(url)

    if video_path is None:
        await update.message.reply_text("⚠️ Couldn't download the video. Maybe it's invalid?")
        return

    try:
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
        os.remove(video_path)
    except Exception as e:
        logging.error("Failed to send video: %s", e)
        await update.message.reply_text("❌ Failed to send the video.")
        


def download_video(url):
    result = {}

    def hook(d):
        if d["status"] == "finished":
            result["filepath"] = d["filename"]

    ydl_opts = {
        "format": "best",
        "max_filesize": 50 * 1024 * 1024,  # 50 MB in bytes
        "outtmpl": "example_videos/%(title)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        'progress_hooks': [hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        logging.error("yt-dlp failed: %s", e)
        return None

    return result.get("filepath")

def check_video_size(url):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filesize = info.get("filesize") or info.get("filesize_approx")

            if not filesize:
                return True, 0  # No size info, assume it's okay

            size_mb = filesize / (1024 * 1024)
            return (size_mb <= 50), size_mb

    except Exception as e:
        logging.error("Failed to check video size: %s", e)
        return False, 0


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