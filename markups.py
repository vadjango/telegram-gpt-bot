from translate import translate
from telebot import types
from telebot.types import ReplyKeyboardMarkup
from typing import Callable
from config import ADMIN_ID, redis_


def markup_main_menu(chat_id: int) -> ReplyKeyboardMarkup:
    _ = translate[redis_.hget(f"user_{chat_id}", "local").decode("utf-8")].gettext
    redis_.hdel(f"user_{chat_id}", "mode")
    redis_.hset(f"user_{chat_id}", "replicas", "")
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # correction of mistakes sucks, will be implemented later
    ask_question = types.KeyboardButton(_('💬 Dialogue'))
    detailed_answer = types.KeyboardButton(_('❔ Detailed answer'))
    instruction = types.KeyboardButton(_("📜 Instruction"))
    change_lang = types.KeyboardButton(_("🌏 Language"))
    if chat_id in ADMIN_ID:
        disable_btn = types.KeyboardButton(_("❌ Disable a bot"))
        kb.add(ask_question, detailed_answer, instruction, change_lang, disable_btn)
    else:
        feedback_btn = types.KeyboardButton(_("🗯 Feedback"))
        kb.add(ask_question, detailed_answer, instruction, change_lang, feedback_btn)
    return kb


def get_dialog_menu(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_new_dial = types.KeyboardButton(_("New dialogue"))
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(start_new_dial, main_menu)
    return kb


def get_detailed_answer_menu(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(main_menu)
    return kb


def create_launch_menu(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_btn = types.KeyboardButton(_("▶ Launch"))
    kb.add(start_btn)
    return kb
