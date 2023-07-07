import os
import gettext
import redislite
import telebot
import logging

_ = gettext.gettext

LOG_FORMAT = "%(asctime)s"

logging.basicConfig(level=logging.INFO, filename="bot.log")

TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")
bot = telebot.TeleBot(TELEBOT_TOKEN, threaded=False)
ADMIN_ID = (1054140400, 975772882)
DB_NAME = "database.db"
TELEGRAM_USERS = "telegram_users"
TELEGRAM_USERS_KEYS = "telegram_users_keys"
LANG = {
    "English": "en_US",
    "Русский": "ru_RU"
}

red = redislite.Redis("/tmp/redis.db")
