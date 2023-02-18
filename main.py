import telebot
import time
import psycopg2
from psycopg2 import IntegrityError
from openai_request import CompletionAI, ExcessTokensException
import sys
from telebot import types, formatting
from telebot.types import ReplyKeyboardMarkup, Message
from telebot.util import quick_markup
from datetime import datetime
from threading import Thread
from bot_users import UserInfo, UserMode
from config import TELEBOT_TOKEN, ADMIN_ID, DB_CONFIG, START_BOT_TEXT

bot = telebot.TeleBot(TELEBOT_TOKEN)
BOT_STOP = False

USERS: dict[int, UserInfo] = {}
KEY_ACTIVE_REQS: dict[str, int] = {}


def _markup_options(chat_id: int) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # correction of mistakes sucks, will be implemented later
    ask_question = types.KeyboardButton('💬 Диалог')
    detailed_answer = types.KeyboardButton('❔ Обширный ответ')
    qt = types.KeyboardButton("🚪 Выход")
    instruction = types.KeyboardButton("📜 Инструкция")
    if chat_id in ADMIN_ID:
        disable_btn = types.KeyboardButton("❌ Отключить бота")
        kb.add(ask_question, detailed_answer, qt, instruction, disable_btn)
    else:
        feedback_btn = types.KeyboardButton("🗯 Обратная связь")
        kb.add(ask_question, detailed_answer, qt, instruction, feedback_btn)
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


@bot.message_handler(func=lambda msg: msg.text == "▶ Запустить")
@bot.message_handler(commands=["start"])
def start(msg, txt=START_BOT_TEXT):
    if msg.text == "▶Запустить":
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    elif msg.text == "/start":
        Thread(target=add_user_to_db, args=(msg.chat.id,), name="user_recording").start()
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id,
                         text=txt,
                         reply_markup=_markup_options(msg.chat.id))
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/TestChannelNotForAnyone"}})
        bot.send_message(chat_id=msg.chat.id,
                         text="Для использования даного телеграм-бота нужно подписаться на телеграм-канал",
                         reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == '❔ Обширный ответ')
def give_a_detailed_answer(msg):
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id,
                         text="В этом режиме бот дает развернутый ответ.",
                         reply_markup=_create_detailed_answer_menu())
        USERS[msg.chat.id] = UserInfo(last_active_datetime=datetime.now(),
                                      mode=UserMode.DETAILED_ANSWER,
                                      has_active_request=False,
                                      replicas="")
        print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Начать диалог' " +
              f"время: {USERS[msg.chat.id]['last_active_datetime'].time()}")
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/TestChannelNotForAnyone"}})
        bot.send_message(chat_id=msg.chat.id,
                         text="Для того, чтобы продолжить использование даного телеграм-бота, нужно подписаться на телеграм-канал",
                         reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == '💬 Диалог')
def ask_a_question(msg):
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id,
                         text="В этом режиме бот может построить логически связанный диалог.",
                         reply_markup=_create_dialog_menu())
        USERS[msg.chat.id] = UserInfo(last_active_datetime=datetime.now(),
                                      mode=UserMode.DIALOG,
                                      has_active_request=False,
                                      replicas="")
        print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Начать диалог' " +

              f"время: {USERS[msg.chat.id]['last_active_datetime'].time()}")
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/TestChannelNotForAnyone"}})
        bot.send_message(chat_id=msg.chat.id,
                         text="Для того, чтобы продолжить использование даного телеграм-бота, нужно подписаться на телеграм-канал",
                         reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == "🗯 Обратная связь")
def show_feedback_names(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text="Если у вас появились трудности в использовании бота, пишите в личные сообщения @osiris_4 и @vadmart")


def _create_launch_menu() -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_btn = types.KeyboardButton("▶ Запустить")
    kb.add(start_btn)
    return kb


@bot.message_handler(func=lambda msg: msg.text == "🚪 Выход")
def exit_the_mode(msg: Message | int) -> None:
    """
    Function which allows user to exit from the bot.
    :param msg - either Message instance or integer. If integer, it represents a chat id
    """
    try:
        if isinstance(msg, Message):
            print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выход")
            bot.send_message(msg.chat.id, "До свидания)", reply_markup=_create_launch_menu())
            del USERS[msg.chat.id]
        else:
            print(f"USER_ID: {msg}: выход")
            bot.send_message(msg, "До свидания)", reply_markup=_create_launch_menu())
            del USERS[msg]
    except KeyError:
        pass


@bot.message_handler(func=lambda msg: msg.text == "❌ Отключить бота")
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
                                 disable_notification=True,
                                 reply_markup=_create_launch_menu())
            except telebot.apihelper.ApiTelegramException:
                pass
    BOT_STOP = True
    bot.stop_bot()
    time.sleep(60)
    sys.exit()


@bot.message_handler(func=lambda msg: msg.text == "📜 Инструкция")
def get_instruction(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text="""
                     Инструкция для бота:
    💬 Диалог - бот дает неразвернутый ответ (хотя его достаточно в большинстве случаев), однако запоминает реплики и, следовательно, понимает контекст. Например, можно спросить "Что такое клетка?", и если после ответа написать боту "Нравится ли тебе она?", он даст ответ касаемо клетки.
    ❔ Обширный ответ - бот не запоминает реплики, то есть, контекста разговора понимать не будет. Однако, максимально возможный ответ может быть в 2 раза больше, чем в режиме "Диалог". Полезно, если Вы не собираетесь развивать тему, однако хотите получить подробный ответ.""")


@bot.message_handler(func=lambda msg: msg.text == "Новый диалог")
def start_new_dialog(msg):
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    try:
        USERS[msg.chat.id]['last_active_datetime'] = datetime.now()
    except KeyError:
        bot.send_message(chat_id=msg.chat.id,
                         text="Выберите режим из главного меню!")
        return
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id, text="Начинаем новый диалог!")
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/TestChannelNotForAnyone"}})
        bot.send_message(chat_id=msg.chat.id,
                         text="Для того, чтобы продолжить использование даного телеграм-бота, нужно подписаться на телеграм-канал",
                         reply_markup=markup)

    print(
        f"{msg.from_user.first_name} {msg.from_user.last_name}: начало нового диалога, время: {USERS[msg.chat.id]['last_active_datetime'].time()}")


@bot.message_handler(func=lambda msg: msg.text == "☰ Главное меню")
def end_dialog(msg):
    try:
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
        start(msg, "Наш прекрасный диалог завершен:).\nВыбери опцию:")
        del USERS[msg.chat.id]
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: завершение диалога, время: {USERS[msg.chat.id]['last_active_datetime'].time()}")
    except KeyError:
        pass


@bot.message_handler(func=lambda _: True)
def handle_requests(msg):
    try:
        if not USERS[msg.chat.id]["has_active_request"]:
            if USERS[msg.chat.id]["mode"] == UserMode.DIALOG:
                bot.send_message(chat_id=msg.chat.id,
                                 text=formatting.hitalic("Запрос отправлен, ожидайте ответа😉"),
                                 parse_mode="HTML")
                Thread(name=f"User {msg.chat.id}", target=send_dialog_request,
                       args=(msg, f"Thread {msg.chat.id}")).start()
            elif USERS[msg.chat.id]["mode"] == UserMode.DETAILED_ANSWER:
                USERS[msg.chat.id]['replicas'] = ""
                Thread(name=f"User {msg.chat.id}", target=send_detailed_request,
                       args=(msg, f"Thread {msg.chat.id}")).start()
        else:
            bot.send_message(chat_id=msg.chat.id,
                             text=formatting.hitalic("Ваш ответ обрабатывается.\nПожалуйста, подождите..."),
                             parse_mode="HTML")
    except KeyError:
        bot.send_message(chat_id=msg.chat.id, text="Выберите режим из главного меню!")


def send_detailed_request(msg: Message, thr_name: str):
    print(f"{thr_name}: старт работы")
    USERS[msg.chat.id]['has_active_request'] = True
    best_api_key = None
    try:
        bot.send_chat_action(msg.chat.id, "typing")
        best_api_key = min(KEY_ACTIVE_REQS.keys(), key=lambda k: KEY_ACTIVE_REQS[k])
        KEY_ACTIVE_REQS[best_api_key] += 1
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: отправка запроса, ключ: {best_api_key}, кол-во токенов: 3200")
        answer = CompletionAI(api_key=best_api_key, txt=msg.text, max_tokens=3200).get_answer()
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: получение ответа")
        USERS[msg.chat.id]['last_active_datetime'] = datetime.now()
        USERS[msg.chat.id]['has_active_request'] = False
        if USERS[msg.chat.id]["mode"] == UserMode.DETAILED_ANSWER:
            # if user's mode hasn't changed while processing the request
            bot.send_message(msg.chat.id, answer)
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: время: {USERS[msg.chat.id]['last_active_datetime'].time()}")
    except (telebot.apihelper.ApiTelegramException, ExcessTokensException) as err:
        USERS[msg.chat.id]['last_active_datetime'] = datetime.now()
        USERS[msg.chat.id]['has_active_request'] = False
        if USERS[msg.chat.id]["mode"] == UserMode.DETAILED_ANSWER:
            if type(err).__name__ == "ApiTelegramException":
                bot.send_message(msg.chat.id, "Не знаю, что и ответить")
            else:
                bot.send_message(msg.chat.id, err)
    except KeyError:
        pass
    finally:
        KEY_ACTIVE_REQS[best_api_key] -= 1
    print(f"{thr_name}: конец работы")


def send_dialog_request(msg: Message, thr_name: str):
    print(f"{thr_name}: старт работы")
    USERS[msg.chat.id]['has_active_request'] = True
    best_api_key = None
    try:
        if not msg.text.endswith((".", "?", "!")):
            msg.text += ".\n"
        else:
            msg.text += "\n"
        USERS[msg.chat.id]['replicas'] += msg.text
        bot.send_chat_action(msg.chat.id, "typing")
        best_api_key = min(KEY_ACTIVE_REQS.keys(), key=lambda k: KEY_ACTIVE_REQS[k])
        KEY_ACTIVE_REQS[best_api_key] += 1
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: отправка запроса, ключ: {best_api_key}, кол-во токенов: 1600")
        answer = CompletionAI(api_key=best_api_key, txt=USERS[msg.chat.id]['replicas'], max_tokens=1600).get_answer()
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: получение ответа")
        USERS[msg.chat.id]['replicas'] += answer + "\n"
        USERS[msg.chat.id]['last_active_datetime'] = datetime.now()
        USERS[msg.chat.id]['has_active_request'] = False
        if USERS[msg.chat.id]["mode"] == UserMode.DIALOG:
            bot.send_message(msg.chat.id, answer, reply_markup=_create_dialog_menu())
        print(
            f"{msg.from_user.first_name} {msg.from_user.last_name}: время: {USERS[msg.chat.id]['last_active_datetime'].time()}")
    except (telebot.apihelper.ApiTelegramException, ExcessTokensException) as err:
        USERS[msg.chat.id]['last_active_datetime'] = datetime.now()
        USERS[msg.chat.id]['has_active_request'] = False
        if USERS[msg.chat.id]["mode"] == UserMode.DIALOG:
            if type(err).__name__ == "ApiTelegramException":
                bot.send_message(msg.chat.id, "Не знаю, что и ответить")
            else:
                bot.send_message(msg.chat.id, err)
    except KeyError:
        pass
    finally:
        KEY_ACTIVE_REQS[best_api_key] -= 1
    print(f"{thr_name}: конец работы")


def _create_dialog_menu() -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_new_dial = types.KeyboardButton("Новый диалог")
    main_menu = types.KeyboardButton("☰ Главное меню")
    kb.add(start_new_dial, main_menu)
    return kb


def _create_detailed_answer_menu() -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu = types.KeyboardButton("☰ Главное меню")
    kb.add(main_menu)
    return kb


def run():
    bot.infinity_polling()


def _delete_user(user_id):
    bot.send_message(chat_id=user_id,
                     text="Вы бездействовали 10 минут, потому диалог завешен автоматически.\nВыберите один из режимов ниже:",
                     reply_markup=_markup_options(user_id))
    del USERS[user_id]


def check_users():
    while True:
        if BOT_STOP:
            return
        for user_id in list(USERS):
            try:
                if (datetime.now() - USERS[user_id]['last_active_datetime']).seconds > 600:
                    _delete_user(user_id)
            except KeyError:
                pass
        time.sleep(1)


def _init_api_keys():
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT OPENAI_API_KEY FROM TELEGRAM_USERS_KEYS")
        for key_tuple in cursor.fetchall():
            KEY_ACTIVE_REQS[key_tuple[0]] = 0


def _init_users():
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT USER_ID FROM TELEGRAM_USERS")
        for user_id_tup in cursor.fetchall():
            try:
                bot.send_message(chat_id=user_id_tup[0],
                                 text="Бот запущен и готов к использованию🙂",
                                 reply_markup=_create_launch_menu())
            except telebot.apihelper.ApiTelegramException:
                pass


if __name__ == "__main__":
    _init_api_keys()
    _init_users()
    Thread(name="user_kicker", target=check_users).start()
    run()
