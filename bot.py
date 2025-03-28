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
import asyncio
import re
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
import logging

API_TOKEN = "7840816964:AAFQLW875DAEDjXSnljfiRCSsMgMcTRMnRg"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Regex for Terabox links
TERABOX_PATTERN = re.compile(
    r"https?://(?:\w+\.)?(terabox|1024terabox|freeterabox|teraboxapp|tera|teraboxlink|mirrorbox|nephobox|1024tera|momerybox|tibibox|terasharelink|teraboxshare|terafileshare)\.\w+"
)

# Function to get download links from the website
def get_download_links(terabox_url):
    session = requests.Session()
    downloader_url = "https://yt.savetube.me/terabox-downloader"

    # Step 1: Get the website's session & form data
    response = session.get(downloader_url)
    if response.status_code != 200:
        return "Failed to connect to the downloader website."

    # Parse the page to find the form token (if needed)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the form action URL (if it's a POST request)
    form_action = downloader_url  # Assuming it's the same URL

    # Step 2: Submit the form with the Terabox link
    form_data = {
        "url": terabox_url,  # The field where we paste the link
    }
    
    submit_response = session.post(form_action, data=form_data)
    
    if submit_response.status_code != 200:
        return "Error submitting the link to the downloader."

    # Step 3: Wait for processing
    asyncio.sleep(10)  # Wait for the site to process

    # Step 4: Parse the download page to extract links
    soup = BeautifulSoup(submit_response.text, "html.parser")

    # Extract "Download video" and "Fast Download" buttons
    download_links = {}
    for button in soup.find_all("a"):
        text = button.text.strip()
        href = button.get("href")
        if "Download video" in text:
            download_links["Download video"] = href
        elif "Fast Download" in text:
            download_links["Fast Download"] = href

    if not download_links:
        return "Failed to retrieve download links. Try again later."

    return download_links


# Telegram bot handlers
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Send me a Terabox link, and I'll fetch the download links for you!")

@dp.message()
async def process_terabox_link(message: Message):
    url_match = TERABOX_PATTERN.search(message.text)
    if not url_match:
        await message.answer("Please send a valid Terabox link.")
        return

    terabox_url = url_match.group()
    
    await message.answer("Processing your request... Please wait 10 seconds.")

    # Fetch the download links
    download_links = get_download_links(terabox_url)

    # Send response
    if isinstance(download_links, dict):
        response_text = "Here are your download links:\n\n"
        for name, link in download_links.items():
            response_text += f"➡️ [{name}]({link})\n"
        await message.answer(response_text, parse_mode="Markdown")
    else:
        await message.answer(download_links)


# Start bot
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
