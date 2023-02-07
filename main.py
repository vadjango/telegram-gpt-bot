from config import *
import telebot
import time
from telebot import types
from telebot.types import ReplyKeyboardMarkup, Message
from datetime import datetime
from threading import Thread

from dotenv import load_dotenv

dotenv_path = "vars.env"
load_dotenv(dotenv_path)
OPTION = None

bot = telebot.TeleBot(os.getenv("TOKEN"))

users_info: dict[list[str, datetime]] = dict()
users_replicas = dict()


def markup_options() -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    corr_mist = types.KeyboardButton("Исправить ошибки")
    ask_question = types.KeyboardButton("Задать вопрос")
    qt = types.KeyboardButton("Выход")
    kb.add(corr_mist, ask_question, qt)
    return kb


@bot.message_handler(func=lambda msg: msg.text == "Запустить")
@bot.message_handler(commands=["start"])
def start(msg, txt="Привет, я телеграм-бот, который способен ответить на все твои вопросы.\nВыбери опцию:"):
    if msg.text == "Запустить":
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    bot.send_message(chat_id=msg.chat.id,
                     text=txt,
                     reply_markup=markup_options())


def correct_mistakes_with_openai(msg: Message, thr_name: str) -> None:
    print(f"{thr_name}: старт работы")
    bot.send_chat_action(msg.chat.id, "typing")
    users_info[msg.chat.id][1] = datetime.now()
    bot.send_message(chat_id=msg.chat.id,
                     text=openai.Edit.create(
                         model="text-davinci-edit-001",
                         input=msg.text,
                         instruction="Fix the spelling mistakes",
                         temperature=0
                     )["choices"][0]["text"]
                     )
    users_info[msg.chat.id][1] = datetime.now()
    print(f"{thr_name}: конец работы")


def send_openai_respond(msg: Message, thr_name: str):
    print(f"{thr_name}: старт работы")
    kb = None
    try:
        try:
            users_replicas[msg.chat.id] += msg.text + "\n"
        except KeyError:
            users_replicas[msg.chat.id] = msg.text + "\n"
        # print(f"Добавление реплики юзера: {users_replicas[msg.chat.id]}")
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_new_dial = types.KeyboardButton("Начать новый диалог")
        end_dial = types.KeyboardButton("Завершить диалог")
        kb.add(start_new_dial, end_dial)
        bot.send_chat_action(msg.chat.id, "typing")
        users_info[msg.chat.id][1] = datetime.now()
        print(f"{msg.from_user.first_name} {msg.from_user.last_name}: отправка запроса")
        answer = openai.Completion.create(
            model="text-davinci-003",
            prompt=users_replicas[msg.chat.id],
            temperature=0.3,
            max_tokens=2048,
            n=1,
            stop=None,
            echo=False
        )["choices"][0]["text"]
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: получение ответа")
        users_replicas[msg.chat.id] += answer + "\n"
        # print(f"Добавление реплики бота: {users_replicas[msg.chat.id]}")
        bot.send_message(msg.chat.id, answer, reply_markup=kb)
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(msg.chat.id, "Не знаю, что и ответить", reply_markup=kb)
    except openai.error.InvalidRequestError:
        bot.send_message(msg.chat.id,
                         "Невозможно отправить сообщение, ибо диалог получился слишком длинным. Нажмите кнопку 'Начать новый диалог', чтобы сбросить текущий диалог",
                         reply_markup=kb)
    finally:
        users_info[msg.chat.id][1] = datetime.now()
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: время: {users_info[msg.chat.id][1].time()}")
    print(f"{thr_name}: конец работы")


@bot.message_handler(func=lambda msg: msg.text == "Исправить ошибки")
def correct_mistakes(msg):
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    bot.send_message(msg.chat.id, "Введи любой текст, я исправлю, если есть ошибки")
    users_info[msg.chat.id] = ["correct_mistakes", datetime.now()]
    print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Исправить ошибки' " +
          f"время: {users_info[msg.chat.id][1].time()}")


@bot.message_handler(func=lambda msg: msg.text == "Задать вопрос")
def ask_a_question(msg):
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    bot.send_message(msg.chat.id, "Пиши что угодно, отвечу, как могу)")
    users_info[msg.chat.id] = ["speak", datetime.now()]
    print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Задать вопрос' " +
          f"время: {users_info[msg.chat.id][1].time()}")


@bot.message_handler(func=lambda msg: msg.text == "Выход")
def exit_the_mode(msg):
    try:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_btn = types.KeyboardButton("Запустить")
        kb.add(start_btn)
        print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выход")
        bot.send_message(msg.chat.id, "До свидания)", reply_markup=kb)
        del users_info[msg.chat.id]
        del users_replicas[msg.chat.id]
    except KeyError:
        pass


@bot.message_handler(func=lambda msg: msg.text == "Начать новый диалог")
def start_new_dialog(msg):
    users_replicas[msg.chat.id] = ""
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    bot.send_message(chat_id=msg.chat.id, text="Начинаем новый диалог!")
    users_info[msg.chat.id][1] = datetime.now()
    print(
        f"{msg.from_user.first_name} {msg.from_user.last_name}: начало нового диалога, время: {users_info[msg.chat.id][1].time()}")


@bot.message_handler(func=lambda msg: msg.text == "Завершить диалог")
def end_dialog(msg):
    try:
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
        start(msg, "Наш прекрасный диалог завершен:).\nВыбери опцию:")
        del users_replicas[msg.chat.id]
        users_info[msg.chat.id][1] = datetime.now()
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: завершение диалога, время: {users_info[msg.chat.id][1].time()}")
    except KeyError:
        pass


@bot.message_handler(func=lambda _: True)
def handle_requests(msg):
    try:
        if users_info[msg.chat.id][0] == "correct_mistakes":
            thr = Thread(target=correct_mistakes_with_openai, args=(msg, f"Thread {msg.chat.id}"), daemon=True)
            thr.start()
        elif users_info[msg.chat.id][0] == "speak":
            thr = Thread(target=send_openai_respond, args=(msg, f"Thread {msg.chat.id}"), daemon=True)
            thr.start()
    except KeyError:
        bot.send_message(msg.chat.id,
                         "Для взаимодействия со мной выбери режим с помощью кнопок, расположенных внизу")


def run():
    bot.infinity_polling()


def check_users():
    while True:
        for user_id in list(users_info):
            if (datetime.now() - users_info[user_id][1]).seconds > 600:
                try:
                    del users_replicas[user_id]
                except KeyError:
                    pass
                print(f"Удаляем {user_id}, время: {users_info[user_id][1].time()}")
                bot.send_message(chat_id=user_id,
                                 text="Вы не взаимодействовали с ботом более 10 минут, поэтому ваши диалоги удалены. Вы можете продолжить работу, выбрав режим",
                                 reply_markup=markup_options(),
                                 disable_notification=True)
                del users_info[user_id]
        time.sleep(1)


if __name__ == "__main__":
    tr = Thread(target=check_users, name="Checking", daemon=True)
    tr.start()
    run()

# TODO: добавить генерацию фотографий (возможно),
#  улечшить поиск ошибок в тексте, реализовать логическую цепочку
