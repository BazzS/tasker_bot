from aiogram import Bot, Dispatcher
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json


#Общие настройки бота
API_TOKEN = '5522342383:AAHUSURDZpnylpRb-K43hkgWYxft3JZgPpw'
storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
#ADMIN = 1739499074
