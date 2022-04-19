import logging
import sqlite3
from config import token
from aiogram import Bot, Dispatcher, executor, types
bot = Bot(token=token)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
con = sqlite3.connect('meetings_data.db')
cur = con.cursor()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('hi')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
