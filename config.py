import os
import logging
from dotenv import load_dotenv
import gettext
import redislite
import telebot

_ = gettext.gettext

load_dotenv("vars.env")
datefmt = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(filename="bot.log", format="%(asctime)s %(levelname)s %(message)s", datefmt=datefmt,
                    level=logging.DEBUG)

TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")
bot = telebot.TeleBot(TELEBOT_TOKEN)
ADMIN_ID = (1054140400, 975772882)
SQLITE_NAME = "database.db"
TABLE_NAME = "telegram_users"
LANG = {
    "English": "en_US",
    "Русский": "ru_RU"
}

redis_ = redislite.Redis("/tmp/redis.db")
