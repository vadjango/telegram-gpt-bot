from config import *
import telebot
from telebot import types

from dotenv import load_dotenv

dotenv_path = "vars.env"
load_dotenv(dotenv_path)
OPTION = None

bot = telebot.TeleBot(os.getenv("TOKEN"))

users_modes = {}


@bot.message_handler(commands=["start"])
def start(msg):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    corr_mist = types.KeyboardButton("Исправить ошибки")
    ask_question = types.KeyboardButton("Задать вопрос")
    qt = types.KeyboardButton("Выход")
    kb.add(corr_mist, ask_question, qt)
    bot.send_message(chat_id=msg.chat.id,
                     text="Привет, я телеграм-бот, который способен ответить на все твои вопросы.\nВыбери опцию:",
                     reply_markup=kb)


def correct_mistakes(text):
    response = openai.Edit.create(
        model="text-davinci-edit-001",
        input=text,
        instruction="Fix the spelling mistakes",
        temperature=0
    )
    return response.choices[0].text


def respond(user_input):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=user_input,
        temperature=0.3,
        max_tokens=2048,
        n=1,
        stop=None,
        echo=False
    )
    print(response)
    return response.choices[0]["text"]


@bot.message_handler(func=lambda _: True)
def send_to_gpt(msg):
    if msg.text == "Исправить ошибки":
        bot.send_message(msg.chat.id, "Введи любой текст, я исправлю, если есть ошибки")
        users_modes[msg.chat.id] = "correct_mistakes"
        return
    elif msg.text == "Задать вопрос":
        bot.send_message(msg.chat.id, "Пиши что угодно, отвечу, как могу)")
        users_modes[msg.chat.id] = "speak"
        return
    elif msg.text == "Выход":
        try:
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_btn = types.KeyboardButton("/start")
            kb.add(start_btn)
            bot.send_message(msg.chat.id, "До свидания)", reply_markup=kb)
            del users_modes[msg.chat.id]
        except KeyError:
            pass
    else:
        try:
            if users_modes[msg.chat.id] == "correct_mistakes":
                bot.send_chat_action(msg.chat.id, "typing")
                answer = correct_mistakes(msg.text)
                bot.send_message(msg.chat.id, answer)
            elif users_modes[msg.chat.id] == "speak":
                bot.send_chat_action(msg.chat.id, "typing")
                answer = respond(msg.text)
                bot.send_message(msg.chat.id, answer)
        except KeyError:
            pass


def run():
    bot.infinity_polling()


if __name__ == "__main__":
    run()

# TODO: добавить генерацию фотографий (возможно),
#  поиск ошибок в тексте
