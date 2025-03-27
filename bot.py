from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup
import re
import aiohttp  # Using aiohttp for async HTTP requests
from web import keep_alive
import logging
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Replace with your Telegram bot token
BOT_TOKEN = "7840816964:AAFQLW875DAEDjXSnljfiRCSsMgMcTRMnRg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Function to get download links from yt.savetube.me
def get_download_links(terabox_url):
    try:
        url = "https://yt.savetube.me/terabox-downloader"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = {"url": terabox_url}

        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")

        # Find the "Download video" and "Fast Download" buttons
        download_video_btn = soup.find("a", string="Download video")
        fast_download_btn = soup.find("a", string="Fast Download")

        download_video_link = download_video_btn["href"] if download_video_btn else None
        fast_download_link = fast_download_btn["href"] if fast_download_btn else None

        return download_video_link, fast_download_link

    except Exception as e:
        logging.error(f"Error fetching links: {e}")
        return None, None

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Send me a Terabox URL, and I'll get the download links for you!")

@dp.message_handler()
async def fetch_links(message: types.Message):
    terabox_url = message.text.strip()

    if "terabox.com" not in terabox_url:
        await message.reply("Please send a valid Terabox URL!")
        return

    await message.reply("Fetching download links, please wait...")

    download_video_link, fast_download_link = get_download_links(terabox_url)

    if not download_video_link and not fast_download_link:
        await message.reply("Failed to get download links. Please try again later.")
        return

    keyboard = InlineKeyboardMarkup()
    if download_video_link:
        keyboard.add(InlineKeyboardButton("Download Video", url=download_video_link))
    if fast_download_link:
        keyboard.add(InlineKeyboardButton("Fast Download", url=fast_download_link))

    await message.reply("Here are your download links:", reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
