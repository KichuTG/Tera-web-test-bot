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
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your Telegram bot token
BOT_TOKEN = "7840816964:AAFQLW875DAEDjXSnljfiRCSsMgMcTRMnRg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Function to get download links from yt.savetube.me
async def get_download_links(terabox_url):
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

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Hello! Send me a Terabox URL, and I'll fetch the download links for you.")

@dp.message(F.text)
async def fetch_links(message: types.Message):
    terabox_url = message.text.strip()

    if "terabox.com" not in terabox_url:
        await message.reply("Please send a valid Terabox URL!")
        return

    waiting_message = await message.reply("Processing your request. Please wait 10 seconds...")

    await asyncio.sleep(10)  # Wait for 10 seconds before fetching the links

    download_video_link, fast_download_link = await get_download_links(terabox_url)

    if not download_video_link and not fast_download_link:
        await waiting_message.edit_text("Failed to get download links. Please try again later.")
        return

    keyboard = InlineKeyboardMarkup()
    if download_video_link:
        keyboard.add(InlineKeyboardButton("Download Video", url=download_video_link))
    if fast_download_link:
        keyboard.add(InlineKeyboardButton("Fast Download", url=fast_download_link))

    await waiting_message.edit_text("Here are your download links:", reply_markup=keyboard)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
 if __name__ == "__main__":
    keep_alive()
    main()
