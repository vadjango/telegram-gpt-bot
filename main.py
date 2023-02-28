import telebot
import time
from openai_interact import *
import sys
from telebot import formatting
from telebot.types import Message
from telebot.util import quick_markup
from threading import Thread, Lock
from db_interaction import *
from markups import *
from bot_users import *
from bottle import run, post, request as bottle_request

bot = telebot.TeleBot(TELEBOT_TOKEN)
STOP_USERS_CHECKER = False
THR_NAME = threading.current_thread().name

lock = Lock()


def init_user(chat_id: int):
    """
    Add a user to database if he doesn't exist (and also adds to USERS), otherwise just add to USERS
    :param chat_id:
    :return: None
    """
    thread_name = threading.current_thread().name
    try:
        add_user_to_database(chat_id)
        logging.info(f"{thread_name} : добавлен юзер {chat_id} в таблицу")
        add_user(chat_id)
    except IntegrityError:
        add_user(chat_id, get_user_loc(chat_id))


def start_in_thread(msg: Message, txt: str):
    thr_name = threading.current_thread().name
    init_user(msg.chat.id)
    _ = translate[USERS[msg.chat.id]['local']].gettext
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id,
                         text=_(txt),
                         reply_markup=markup_main_menu(msg.chat.id))
        logging.info(f"{thr_name} : {msg.from_user.first_name} {msg.from_user.last_name}: начало работы")
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/ChatGPTBOT_channel"}})
        bot.send_message(chat_id=msg.chat.id,
                         text=_("In order to use this bot, you need to subscribe telegram channel"),
                         reply_markup=markup)
        del USERS[msg.chat.id]
        logging.info(
            f"{thr_name} : {msg.from_user.first_name} {msg.from_user.last_name}: требуется подписка на телеграм-канал")


@bot.message_handler(func=lambda msg: msg.text in ("▶ Launch", "▶ Запустить"))
@bot.message_handler(commands=["start"])
def start(msg: Message, txt="Hello, I'm a smart bot 🤖\nMy ability is to answer user questions👤\n"
                            "What topics can I touch on? In fact, almost any, preferably not related to "
                            "politicians. Why? The fact is that I am not ideologically tied to any country. "
                            "So your opinion may differ from mine.\n"
                            "To start working with me, select the option:"):
    Thread(name="StartUserThread", target=start_in_thread, args=(msg, txt)).start()


@bot.message_handler(
    func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext('❔ Detailed answer'))
def give_a_detailed_answer(msg):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    USERS[msg.chat.id]['replicas'] = ""
    # bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id,
                         text=_("Bot gives a detailed answer in this mode."),
                         reply_markup=get_detailed_answer_menu(USERS[msg.chat.id]['local']))
        USERS[msg.chat.id]['mode'] = UserMode.DETAILED_ANSWER
        logging.info(
            f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Обширный ответ'")
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/ChatGPTBOT_channel"}})
        bot.send_message(chat_id=msg.chat.id,
                         text=_("In order to continue using this bot, you need to subscribe telegram channel"),
                         reply_markup=markup)
        logging.info(
            f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: требуется подписка на телеграм-канал")


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext('💬 Dialogue'))
def start_first_dialog(msg):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    # bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id,
                         text=_("Bot can build a dialogue with logically connected replicas in this mode."),
                         reply_markup=get_dialog_menu(USERS[msg.chat.id]['local']))
        USERS[msg.chat.id]['mode'] = UserMode.DIALOG
        logging.info(
            f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: выбран режим 'Начать диалог' ")
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/ChatGPTBOT_channel"}})
        bot.send_message(chat_id=msg.chat.id,
                         text=_("In order to continue using this bot, you need to subscribe telegram channel"),
                         reply_markup=markup)
        logging.info(
            f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: требуется подписка на телеграм-канал")


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext("🗯 Feedback"))
def show_feedback_names(msg):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    bot.send_message(chat_id=msg.chat.id,
                     text=_("If you have some issues with using this bot, please contact @osiris_4 и @vadmart"))
    logging.info(
        f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: просмотр контактов для обратной связи")


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext("🌏 Language"))
def change_language(msg):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*(types.KeyboardButton(text=txt) for txt in LANG.keys() if LANG[txt] != USERS[msg.chat.id]['local']))
    bot.send_message(chat_id=msg.chat.id, text=_("Choose language:"), reply_markup=kb)


@bot.message_handler(func=lambda msg: msg.text in LANG.keys())
def choose_lang_for_user(msg):
    Thread(name="user_locale_changing", target=_change_locale_in_db, args=(msg.chat.id, LANG[msg.text])).start()
    USERS[msg.chat.id]['local'] = LANG[msg.text]
    _ = translate[USERS[msg.chat.id]['local']].gettext
    bot.send_message(chat_id=msg.chat.id,
                     text=_("Chosen language: {lng}").format(lng=msg.text),
                     reply_markup=markup_main_menu(msg.chat.id))


def _change_locale_in_db(user_id, lng):
    thr_name = threading.current_thread().name
    if lng not in LANG.values():
        raise ValueError(f"Locale must be selected from given: {LANG.keys()}")
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE test_telegram_users
                          SET locale = %s
                          WHERE user_id = %s""", (lng, user_id))
        conn.commit()
        logging.info(f"{thr_name} : {user_id}: локаль изменена на {lng}")


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext("🚪 Exit"))
def exit_the_mode(msg: Message | int) -> None:
    """
    Function which allows user to exit from the bot.
    :param msg: either Message instance or integer. If integer, it represents a chat id
    """
    _ = translate[USERS[msg.chat.id]['local']].gettext
    try:
        if isinstance(msg, Message):
            print(f"{msg.from_user.first_name} {msg.from_user.last_name}: выход")
            bot.send_message(msg.chat.id, _("Goodbye 👋"),
                             reply_markup=create_launch_menu(USERS[msg.chat.id]['local']))
            del USERS[msg.chat.id]
            logging.info(f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: выход")
        else:
            print(f"USER_ID: {msg}: выход")
            bot.send_message(msg, _("Goodbye 👋"), reply_markup=create_launch_menu(USERS[msg]['local']))
            del USERS[msg]
            logging.info(f"{THR_NAME} : USER_ID {msg}: выход")
    except KeyError:
        pass


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext("❌ Disable a bot"))
def disable_bot_menu(msg):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    markup = quick_markup({_("1 minute"): {"callback_data": "1 minute"},
                           _("5 minutes"): {"callback_data": "5 minutes"},
                           _("10 minutes"): {"callback_data": "10 minutes"},
                           _("20 minutes"): {"callback_data": "20 minutes"}})
    bot.send_message(chat_id=msg.chat.id,
                     text=_("For how long do you want to disable the bot?"),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def bot_disabler(call):
    global STOP_USERS_CHECKER
    all_users = get_all_user_ids_and_languages()
    logging.warning(f"{THR_NAME} : Отправка пользователям информации о ПРЕДСТОЯЩЕМ отключении бота")
    for user_id, loc in all_users:
        _ = translate[loc].gettext
        try:
            bot.send_message(chat_id=user_id,
                             text=_("Bot will be disabled in {data} for further impovements").format(
                                 data=_(call.data)),
                             disable_notification=True)
        except telebot.apihelper.ApiTelegramException:
            pass
    minutes_amount = float(call.data.split()[0])
    logging.warning(f"{THR_NAME} : Отключение бота через {minutes_amount} минут")
    time.sleep(minutes_amount * 60)
    logging.warning(f"{THR_NAME} : Отправка пользователям информации об отключении бота")
    all_users = get_all_user_ids_and_languages()
    for user_id, loc in all_users:
        _ = translate[loc].gettext
        try:
            bot.send_message(chat_id=user_id,
                             text=_("Bot has been disabled for further improvements").format(
                                 data=_(call.data)),
                             disable_notification=True)
        except telebot.apihelper.ApiTelegramException:
            pass
    STOP_USERS_CHECKER = True
    bot.stop_bot()
    logging.warning(f"{THR_NAME} : Бот отключен")
    time.sleep(10)
    sys.exit()


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext("📜 Instruction"))
def get_instruction(msg: Message):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    bot.send_message(chat_id=msg.chat.id,
                     text=_("""
                     Bot instruction:
     💬 Dialogue - the bot gives a non-detailed answer (although it is enough in most cases), but remembers replicas and, therefore, understands the context. For example, you can ask "What is a cell?", and if  you write to the bot "Do you like it?" after the answer, it will give an information about the cell.
     ❔ Detailed answer - the bot does not remember replicas, that is, it will not understand the context of the conversation. However, the maximum possible answer can be 2 times more than in the "Dialogue" mode. Useful if you are not going to develop the topic, but want to get a detailed answer."""))
    logging.info(f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: просмотр инструкции")


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext("New dialogue"))
def start_new_dialog(msg):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
    try:
        USERS[msg.chat.id]['last_active_datetime'] = datetime.now()
    except KeyError:
        bot.send_message(chat_id=msg.chat.id,
                         text=_("Choose the mode from the main menu!"))
        return
    if bot.get_chat_member(chat_id=-1001857064307, user_id=msg.chat.id).status in (
            "member", "creator", "administrator"):
        bot.send_message(chat_id=msg.chat.id, text=_("Start a new dialogue!"))
        logging.info(f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: начало нового диалога")
    else:
        markup = quick_markup({"ChatGPTBOT_channel": {"url": "https://t.me/ChatGPTBOT_channel"}})
        bot.send_message(chat_id=msg.chat.id,
                         text=_("In order to continue using this bot, you need to subscribe telegram channel"),
                         reply_markup=markup)
        logging.info(
            f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: требуется подписка на телеграм-канал")


@bot.message_handler(func=lambda msg: msg.text == translate[USERS[msg.chat.id]['local']].gettext("☰ Main menu"))
def end_dialog(msg):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    try:
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
        start(msg, _("Our beautiful dialogue is over🙂.\nChoose the option:"))
        logging.info(f"{THR_NAME} : {msg.from_user.first_name} {msg.from_user.last_name}: завершение диалога")
    except KeyError:
        pass


@bot.message_handler(content_types=["text"])
def handle_requests(msg: Message):
    _ = translate[USERS[msg.chat.id]['local']].gettext
    try:
        if not USERS[msg.chat.id]["has_active_request"]:
            if USERS[msg.chat.id]["mode"] == UserMode.DIALOG:
                bot.send_message(chat_id=msg.chat.id,
                                 text=formatting.hitalic(_("The request was sent, wait for an answer...😉")),
                                 parse_mode="HTML")
                Thread(name=f"Thread {msg.chat.id}", target=send_request,
                       args=(msg, UserMode.DIALOG)).start()
            elif USERS[msg.chat.id]["mode"] == UserMode.DETAILED_ANSWER:
                bot.send_message(chat_id=msg.chat.id,
                                 text=formatting.hitalic(_("The request was sent, wait for an answer...😉")),
                                 parse_mode="HTML")
                Thread(name=f"Thread {msg.chat.id}", target=send_request,
                       args=(msg, UserMode.DETAILED_ANSWER)).start()
        else:
            bot.send_message(chat_id=msg.chat.id,
                             text=formatting.hitalic(_("Your answer is processing.\nPlease, wait…")),
                             parse_mode="HTML")
    except KeyError:
        bot.send_message(chat_id=msg.chat.id, text=_("Choose the mode from the main menu!"))
        logging.error(f"{THR_NAME} : Пользователь id = {msg.chat.id} не найден!")


def send_request(msg: Message, mode: UserMode) -> Optional[Message]:
    _ = translate[USERS[msg.chat.id]['local']].gettext
    thread_name = threading.current_thread().name
    logging.info(f"{thread_name} : старт работы")
    USERS[msg.chat.id]['has_active_request'] = True
    bot.send_chat_action(msg.chat.id, "typing")
    best_api_key: OpenAIAPIKey = min(OpenAIAPIKey.get_all_keys(), key=lambda k: k.active_reqs_amount)
    with lock:
        best_api_key.increment_active_reqs_amount()
    logging.info(
        f"{thread_name} : {msg.from_user.first_name} {msg.from_user.last_name}: отправка запроса, ключ: {best_api_key.value}, кол-во токенов: 1600")
    try:
        if mode == UserMode.DIALOG:
            USERS[msg.chat.id]['replicas'] += msg.text + "\n"
            answer = CompletionAI(api_key=best_api_key, txt=USERS[msg.chat.id]['replicas'],
                                  max_tokens=1600).get_answer()
            if USERS[msg.chat.id]["mode"] == UserMode.DIALOG:
                # если после получения ответа пользователь не изменил режим
                USERS[msg.chat.id]['replicas'] += answer + "\n"
                return bot.send_message(msg.chat.id, answer, reply_markup=get_dialog_menu(USERS[msg.chat.id]['local']))
        else:
            # режим обширный ответ
            answer = CompletionAI(api_key=best_api_key, txt=msg.text, max_tokens=3200).get_answer()
            if USERS[msg.chat.id]["mode"] == UserMode.DETAILED_ANSWER:
                return bot.send_message(msg.chat.id, answer, reply_markup=get_dialog_menu(USERS[msg.chat.id]['local']))
        logging.info(
            f"{thread_name} : {msg.from_user.first_name} {msg.from_user.last_name}: получение ответа")
    except (telebot.apihelper.ApiTelegramException, ExcessTokensException) as err:
        if type(err).__name__ == "ApiTelegramException":
            bot.send_message(msg.chat.id, _("I don't know what to answer"))
            logging.info(
                f"{thread_name} : {msg.from_user.first_name} {msg.from_user.last_name}: бот ответил пустым сообщением")
        else:
            bot.send_message(msg.chat.id, err)
            logging.info(
                f"{thread_name} : {msg.from_user.first_name} {msg.from_user.last_name}: {err}")
    except KeyError:
        pass
    finally:
        with lock:
            best_api_key.decrement_active_reqs_amount()
        USERS[msg.chat.id]['last_active_datetime'] = datetime.now()
        USERS[msg.chat.id]['has_active_request'] = False
    logging.info(f"{thread_name} : конец работы")


def _worker_users_kicker():
    thread_name = threading.current_thread().name
    logging.info(f"{thread_name} : старт работы")
    while True:
        if STOP_USERS_CHECKER:
            return
        for user_id in list(USERS):
            try:
                if (datetime.now() - USERS[user_id]['last_active_datetime']).seconds > 600:
                    _ = translate[USERS[user_id]['local']].gettext
                    bot.send_message(chat_id=user_id,
                                     text=_(
                                         "You have been inactive for 10 minutes, so the dialog ends automatically.\nChoose one of the modes below:"),
                                     reply_markup=markup_main_menu(user_id))
                    del USERS[user_id]
            except KeyError:
                pass
        time.sleep(1)


def init_api_keys():
    for key_name in get_all_api_keys():
        # инициализация конкретного АПИ-ключа и добавление его в экземпляр класса OpenAIAPIKey
        OpenAIAPIKey(key_name).save_key()


def launch():
    for user_id in get_all_user_ids():
        try:
            _ = translate[USERS[user_id]['local']].gettext
            bot.send_message(chat_id=user_id,
                             text=_("Bot has been launched and is ready to use🙂"),
                             reply_markup=create_launch_menu(USERS[user_id]['local']))
        except telebot.apihelper.ApiTelegramException:
            pass


if __name__ == "__main__":
    init_api_keys()
    logging.info(f"{THR_NAME} : API-ключи успешно инициализированы")
    Thread(name="user_kicker", target=_worker_users_kicker).start()
    # launch() will be active later
    # bot.run_webhooks(listen="localhost",
    #                  port=80,
    #                  webhook_url="https://9aa7-178-150-167-216.eu.ngrok.io")
    bot.polling()
