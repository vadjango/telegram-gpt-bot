import os
import logging
from dotenv import load_dotenv
import gettext
import redis
import telebot

_ = gettext.gettext

load_dotenv("vars.env")
datefmt = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(filename="bot.log", format="%(asctime)s %(levelname)s %(message)s", datefmt=datefmt,
                    level=logging.DEBUG)

TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")
bot = telebot.TeleBot(TELEBOT_TOKEN)
ADMIN_ID = (1054140400, 975772882)
DB_NAME = "database.db"
TELEGRAM_USERS = "telegram_users"
TELEGRAM_USERS_KEYS = "telegram_users_keys"
LANG = {
    "English": "en_US",
    "Русский": "ru_RU"
}

redis_ = redis.Redis(host=os.getenv("REDIS_HOST"),
                     port=6379,
                     password=os.getenv("REDIS_PASSWORD"))
