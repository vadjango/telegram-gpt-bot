import telebot
import time
import psycopg2
from psycopg2 import IntegrityError
from openai_request import CompletionAI, ExcessTokensException
import sys
from telebot import types
from telebot.types import ReplyKeyboardMarkup, Message
from telebot.util import quick_markup
from datetime import datetime
from threading import Thread
from typing import Union
from config import TELEBOT_TOKEN, ADMIN_ID, DB_CONFIG

bot = telebot.TeleBot(TELEBOT_TOKEN)
BOT_STOP = False

USERS_INFO: dict[int, dict[str, Union[datetime, str, bool]]] = dict()
USERS_REPLICAS = dict()
REQUESTS_FOR_KEY = dict()


def markup_options(chat_id) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # correction of mistakes sucks, will be implemented later
    ask_question = types.KeyboardButton('Режим: "Диалог"')
    detailed_answer = types.KeyboardButton('Режим: "Обширный ответ"')
    qt = types.KeyboardButton("Выход")
    if chat_id in ADMIN_ID:
        disable_btn = types.KeyboardButton("Отключить бота")
        kb.add(ask_question, detailed_answer, qt, disable_btn)
    else:
        feedback_btn = types.KeyboardButton("Обратная связь")
        kb.add(ask_question, detailed_answer, qt, feedback_btn)
    return kb


def add_user_to_db(chat_id: int):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                            INSERT INTO telegram_users
                            VALUES (%s)""", (chat_id,))
            conn.commit()
            print(f"Добавлен юзер {chat_id} в таблицу")
    except IntegrityError:
        pass


@bot.message_handler(func=lambda msg: msg.text == "Запустить")
@bot.message_handler(commands=["start"])
def start(msg, txt="Привет, я телеграм-бот, который способен ответить на все твои вопросы.\nВыбери опцию:"):
    if msg.text == "Запустить":
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    elif msg.text == "/start":
        Thread(target=add_user_to_db, args=(msg.chat.id,), name="user_recording").start()
    bot.send_message(chat_id=msg.chat.id,
                     text=txt,
                     reply_markup=markup_options(msg.chat.id))


@bot.message_handler(func=lambda msg: msg.text == 'Режим: "Обширный ответ"')
def give_a_detailed_answer(msg):
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    bot.send_message(msg.chat.id, "В этом режиме бот не запоминает реплики, но дает развернутый ответ")
    USERS_INFO[msg.chat.id] = {"datetime": datetime.now(), "mode": "detailed_answer", "has_sent_request": False}
    print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Начать диалог' " +
          f"время: {USERS_INFO[msg.chat.id]['datetime'].time()}")


@bot.message_handler(func=lambda msg: msg.text == 'Режим: "Диалог"')
def ask_a_question(msg):
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    bot.send_message(msg.chat.id, "Пиши, что угодно, отвечу, как могу)")
    USERS_INFO[msg.chat.id] = {"datetime": datetime.now(), "mode": "dialog", "has_sent_request": False}
    print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Начать диалог' " +
          f"время: {USERS_INFO[msg.chat.id]['datetime'].time()}")


@bot.message_handler(func=lambda msg: msg.text == "Обратная связь")
def show_feedback_names(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text="Если у вас появились трудности в использовании бота, пишите в личные сообщения @osiris_4 и @vadmart")


@bot.message_handler(func=lambda msg: msg.text == "Выход")
def exit_the_mode(msg):
    try:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_btn = types.KeyboardButton("Запустить")
        kb.add(start_btn)
        print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выход")
        bot.send_message(msg.chat.id, "До свидания)", reply_markup=kb)
        del USERS_INFO[msg.chat.id]
        del USERS_REPLICAS[msg.chat.id]
    except KeyError:
        pass


@bot.message_handler(func=lambda msg: msg.text == "Отключить бота")
def disable_bot_menu(msg):
    markup = quick_markup({"1 минуту": {"callback_data": "1"},
                           "5 минут": {"callback_data": "5"},
                           "10 минут": {"callback_data": "10"},
                           "20 минут": {"callback_data": "20"}})
    bot.send_message(chat_id=msg.chat.id,
                     text="На какое время вы хотите отключить бота?",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def bot_disabler(call):
    global BOT_STOP
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telegram_users")
        for user_id_tuple in cursor.fetchall():
            try:
                bot.send_message(chat_id=user_id_tuple[0],
                                 text=f"Бот будет отключен через {call.data} минут для дальнейших доработок",
                                 disable_notification=True)
            except telebot.apihelper.ApiTelegramException:
                pass
    time.sleep(int(call.data) * 60)
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telegram_users")
        for user_id_tuple in cursor.fetchall():
            try:
                bot.send_message(chat_id=user_id_tuple[0],
                                 text=f"Бот отключен для дальнейших доработок",
                                 disable_notification=True)
            except telebot.apihelper.ApiTelegramException:
                pass
    BOT_STOP = True
    bot.stop_bot()
    time.sleep(120)
    sys.exit()


@bot.message_handler(func=lambda msg: msg.text == "Новый диалог")
def start_new_dialog(msg):
    USERS_REPLICAS[msg.chat.id] = ""
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    bot.send_message(chat_id=msg.chat.id, text="Начинаем новый диалог!")
    USERS_INFO[msg.chat.id]["datetime"] = datetime.now()
    print(
        f"{msg.from_user.first_name} {msg.from_user.last_name}: начало нового диалога, время: {USERS_INFO[msg.chat.id]['datetime'].time()}")


@bot.message_handler(func=lambda msg: msg.text == "Главное меню")
def end_dialog(msg):
    try:
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
        start(msg, "Наш прекрасный диалог завершен:).\nВыбери опцию:")
        del USERS_REPLICAS[msg.chat.id]
        del USERS_INFO[msg.chat.id]
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: завершение диалога, время: {USERS_INFO[msg.chat.id]['datetime'].time()}")
    except KeyError:
        pass


@bot.message_handler(func=lambda _: True)
def handle_requests(msg):
    try:
        if not USERS_INFO[msg.chat.id]["has_sent_request"]:
            if USERS_INFO[msg.chat.id]["mode"] == "dialog":
                Thread(name=f"User {msg.chat.id}", target=send_dialog_request, args=(msg, f"Thread {msg.chat.id}")).start()
            elif USERS_INFO[msg.chat.id]["mode"] == "detailed_answer":
                Thread(name=f"User {msg.chat.id}", target=send_detailed_request, args=(msg, f"Thread {msg.chat.id}")).start()
        else:
            bot.send_message(chat_id=msg.chat.id, text="Ваш ответ обрабатывается.\nПожалуйста, подождите ответа...")
    except KeyError:
        bot.send_message(chat_id=msg.chat.id, text="Выберите режим из представленных ниже!")


def send_detailed_request(msg: Message, thr_name: str):
    print(f"{thr_name}: старт работы")
    USERS_INFO[msg.chat.id]["has_sent_request"] = True
    best_api_key = None
    try:
        if not msg.text.endswith((".", "?", "!")):
            msg.text += ". "
        else:
            msg.text += " "
        bot.send_chat_action(msg.chat.id, "typing")
        best_api_key = min(REQUESTS_FOR_KEY.keys(), key=lambda k: REQUESTS_FOR_KEY[k])
        REQUESTS_FOR_KEY[best_api_key] += 1
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: отправка запроса, ключ: {best_api_key}, кол-во токенов: 3200")
        answer = CompletionAI(api_key=best_api_key, txt=msg.text, max_tokens=3200).get_answer()
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: получение ответа")
        bot.send_message(msg.chat.id, answer)
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(msg.chat.id, "Не знаю, что и ответить")
    except ExcessTokensException as e:
        bot.send_message(msg.chat.id, e)
    finally:
        REQUESTS_FOR_KEY[best_api_key] -= 1
        USERS_INFO[msg.chat.id]["datetime"] = datetime.now()
        USERS_INFO[msg.chat.id]["has_sent_request"] = False
    print(
        f"{msg.from_user.first_name} {msg.from_user.last_name}: время: {USERS_INFO[msg.chat.id]['datetime'].time()}")
    print(f"{thr_name}: конец работы")


def send_dialog_request(msg: Message, thr_name: str):
    print(f"{thr_name}: старт работы")
    USERS_INFO[msg.chat.id]["has_sent_request"] = True
    best_api_key = None
    try:
        if not msg.text.endswith((".", "?", "!")):
            msg.text += ". "
        else:
            msg.text += " "
        try:
            USERS_REPLICAS[msg.chat.id] += msg.text
        except KeyError:
            USERS_REPLICAS[msg.chat.id] = msg.text
        bot.send_chat_action(msg.chat.id, "typing")
        best_api_key = min(REQUESTS_FOR_KEY.keys(), key=lambda k: REQUESTS_FOR_KEY[k])
        REQUESTS_FOR_KEY[best_api_key] += 1
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: отправка запроса, ключ: {best_api_key}, кол-во токенов: 1600")
        answer = CompletionAI(api_key=best_api_key, txt=USERS_REPLICAS[msg.chat.id], max_tokens=1600).get_answer()
        REQUESTS_FOR_KEY[best_api_key] -= 1
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: получение ответа")
        USERS_REPLICAS[msg.chat.id] += answer + "\n\n"
        bot.send_message(msg.chat.id, answer, reply_markup=create_dialog_menu())
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(msg.chat.id, "Не знаю, что и ответить", reply_markup=create_dialog_menu())
    except ExcessTokensException as e:
        bot.send_message(msg.chat.id, e)
    finally:
        REQUESTS_FOR_KEY[best_api_key] -= 1
        USERS_INFO[msg.chat.id]["datetime"] = datetime.now()
        USERS_INFO[msg.chat.id]["has_sent_request"] = False
    print(
        f"{msg.from_user.first_name} {msg.from_user.last_name}: время: {USERS_INFO[msg.chat.id]['datetime'].time()}")
    print(f"{thr_name}: конец работы")


def create_dialog_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_new_dial = types.KeyboardButton("Новый диалог")
    end_dial = types.KeyboardButton("Главное меню")
    kb.add(start_new_dial, end_dial)
    return kb


def run():
    bot.infinity_polling()


def _delete_user_replicas(user_id):
    bot.send_message(chat_id=user_id,
                     text="Вы бездействовали 10 минут, потому предыдущие реплики удалены. Вы можете начать диалог сначала")
    del USERS_REPLICAS[user_id]


def check_users():
    while True:
        if BOT_STOP:
            return
        for user_id in USERS_INFO:
            if (datetime.now() - USERS_INFO[user_id]["datetime"]).seconds > 600:
                if user_id in USERS_REPLICAS:
                    _delete_user_replicas(user_id)


def _init_api_keys():
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT OPENAI_API_KEY FROM TELEGRAM_USERS_KEYS")
        for key_tuple in cursor.fetchall():
            REQUESTS_FOR_KEY[key_tuple[0]] = 0


if __name__ == "__main__":
    _init_api_keys()
    Thread(name="user_kicker", target=check_users)
    run()

# TODO: добавить генерацию фотографий (возможно)


# def correct_mistakes_with_openai(msg: Message, thr_name: str) -> None:
#     print(f"{thr_name}: старт работы")
#     bot.send_chat_action(msg.chat.id, "typing")
#     USERS_DT[msg.chat.id] = datetime.now()
#     # bot.send_message(chat_id=msg.chat.id,
#     #                  text=openai.Edit.create(
#     #                      model="text-davinci-edit-001",
#     #                      input=msg.text,
#     #                      instruction="Fix the spelling mistakes",
#     #                      temperature=0
#     #                  )["choices"][0]["text"]
#     #                  )
#     USERS_DT[msg.chat.id] = datetime.now()
#     print(f"{thr_name}: конец работы")

# @bot.message_handler(func=lambda msg: msg.text == "Исправить ошибки")
# def correct_mistakes(msg):
#     bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
#     bot.send_message(msg.chat.id, "Введи любой текст, я исправлю, если есть ошибки")
#     USERS_INFO[msg.chat.id] = datetime.now()
#     print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Исправить ошибки' " +
#           f"время: {USERS_INFO[msg.chat.id].time()}")
