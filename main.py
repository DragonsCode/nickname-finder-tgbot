import asyncio
from pathlib import Path
import requests
import urllib.parse
from bs4 import BeautifulSoup

from aiogram import Bot, Dispatcher, executor, types
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import time
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ChatType

import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TOKEN')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def finder(nickname):
    results = []
    with open(Path(__file__).with_name('text.txt'), encoding='utf-8') as sites:
        for site in sites:
            parts = site.split()
            if len(parts) < 2:
                continue
            url = parts[1] + urllib.parse.quote(nickname, safe='')
            try:
                response = await asyncio.to_thread(requests.get, url, timeout=10)
                prefix = "найден " if response.status_code == 200 else "не найден "
                results.append(prefix + nickname + ": " + url)
            except requests.RequestException:
                results.append("ошибка поиска по " + nickname)
    return results

@dp.message_handler(chat_type=ChatType.PRIVATE)
async def start(message: types.Message):
    finded = await finder(message.text)
    b=''
    for i in finded:
        b+=i+"\n"
    await message.reply(b)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)