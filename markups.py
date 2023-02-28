from translate import translate
from telebot import types
from telebot.types import ReplyKeyboardMarkup
from bot_users import USERS
from config import ADMIN_ID


def markup_main_menu(chat_id: int) -> ReplyKeyboardMarkup:
    _ = translate[USERS[chat_id]['local']].gettext
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # correction of mistakes sucks, will be implemented later
    ask_question = types.KeyboardButton(_('💬 Dialogue'))
    detailed_answer = types.KeyboardButton(_('❔ Detailed answer'))
    qt = types.KeyboardButton(_("🚪 Exit"))
    instruction = types.KeyboardButton(_("📜 Instruction"))
    change_lang = types.KeyboardButton(_("🌏 Language"))
    if chat_id in ADMIN_ID:
        disable_btn = types.KeyboardButton(_("❌ Disable a bot"))
        kb.add(ask_question, detailed_answer, qt, instruction, change_lang, disable_btn)
    else:
        feedback_btn = types.KeyboardButton(_("🗯 Feedback"))
        kb.add(ask_question, detailed_answer, qt, instruction, change_lang, feedback_btn)
    return kb


def get_dialog_menu(lang: str) -> ReplyKeyboardMarkup:
    _ = translate[lang].gettext
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_new_dial = types.KeyboardButton(_("New dialogue"))
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(start_new_dial, main_menu)
    return kb


def get_detailed_answer_menu(lang: str) -> ReplyKeyboardMarkup:
    _ = translate[lang].gettext
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(main_menu)
    return kb


def create_launch_menu(lang: str) -> ReplyKeyboardMarkup:
    _ = translate[lang].gettext
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_btn = types.KeyboardButton(_("▶ Launch"))
    kb.add(start_btn)
    return kb
