import os
from dotenv import load_dotenv
import gettext
import redislite
import telebot
import logging

_ = gettext.gettext

load_dotenv("vars.env")
datefmt = "%d/%m/%Y %H:%M:%S"

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

redis_ = redislite.Redis("/tmp/redis.db")
