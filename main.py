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

finded=[]
async def finder(nickname):
    sites = open('text.txt')
    for site in sites:
        name = site.split(' ')[0]
        link = site.split(' ')[1]
        link = link.rstrip('\n')
        url = link+nickname
        try:
            r = requests.get(url)
            if r.status_code == 200:
                finded.append("найден "+nickname+": "+url)
                print("найден "+nickname+": "+url)
            else:
                finded.append("не найден "+nickname+": "+url)
                print("не найден "+nickname+": "+url)
        except:
            finded.append("ошибка поиска по "+nickname)
            print("ошибка поиска по "+nickname)
    sites.close()

@dp.message_handler(chat_type=ChatType.PRIVATE)
async def start(message: types.Message):
    await finder(message.text)
    b=''
    for i in finded:
        b+=i+"\n"
    await message.reply(b)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)