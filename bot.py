from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup
import re
import aiohttp  # Using aiohttp for async HTTP requests
from web import keep_alive
import logging
import requests
from bs4 import BeautifulSoup
import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your Telegram bot token
BOT_TOKEN = "7840816964:AAFQLW875DAEDjXSnljfiRCSsMgMcTRMnRg"

# Terabox URL pattern
TERABOX_PATTERN = r"https?://(?:\w+\.)?(terabox|1024terabox|freeterabox|teraboxapp|tera|teraboxlink|mirrorbox|nephobox|1024tera|momerybox|tibibox|terasharelink|teraboxshare|terafileshare)\.\w+"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Function to get download links from yt.savetube.me (with retries)
async def get_download_links(terabox_url, max_retries=12, delay=5):
    """Tries to get the download links multiple times, waiting for them to be available."""
    url = "https://yt.savetube.me/terabox-downloader"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = {"url": terabox_url}

    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, data=data)

        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")

        # Find the "Download video" and "Fast Download" buttons
        download_video_btn = soup.find("a", string="Download video")
        fast_download_btn = soup.find("a", string="Fast Download")

        if download_video_btn or fast_download_btn:
            return (
                download_video_btn["href"] if download_video_btn else None,
                fast_download_btn["href"] if fast_download_btn else None
            )

        await asyncio.sleep(delay)  # Wait before retrying

    return None, None  # Return None if links never appear

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Hello! Send me a valid Terabox URL, and I'll fetch the download links for you.")

@dp.message(F.text)
async def fetch_links(message: types.Message):
    terabox_url = message.text.strip()

    # Validate the URL using regex
    if not re.match(TERABOX_PATTERN, terabox_url):
        await message.reply("❌ Invalid Terabox URL! Please send a valid link.")
        return

    waiting_message = await message.reply("⏳ Processing your request. This may take up to **1 minute**...")

    download_video_link, fast_download_link = await get_download_links(terabox_url)

    if not download_video_link and not fast_download_link:
        await waiting_message.edit_text("⚠️ Failed to get download links. Please try again later.")
        return

    keyboard = InlineKeyboardMarkup()
    if download_video_link:
        keyboard.add(InlineKeyboardButton("📥 Download Video", url=download_video_link))
    if fast_download_link:
        keyboard.add(InlineKeyboardButton("⚡ Fast Download", url=fast_download_link))

    await waiting_message.edit_text("✅ Here are your download links:", reply_markup=keyboard)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # Ensures old updates don't cause errors
    await dp.start_polling(bot)  # Starts bot in polling mode

if __name__ == "__main__":
    asyncio.run(main())  # Runs the bot
    keep_alive()
    main()
