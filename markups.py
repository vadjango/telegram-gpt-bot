from translate import translate
from telebot import types
from telebot.types import ReplyKeyboardMarkup
from typing import Callable
from config import ADMIN_ID, red
from db_interaction import get_user_translator


def markup_main_menu(chat_id: int) -> ReplyKeyboardMarkup:
    _ = get_user_translator(chat_id)
    red.hdel(f"user_{chat_id}", "mode")
    red.hset(f"user_{chat_id}", "replicas", "")
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    ask_question = types.KeyboardButton(_('💬 Dialogue'))
    detailed_answer = types.KeyboardButton(_('❔ Detailed answer'))
    solving_tasks = types.KeyboardButton(_("📝 Solving tasks"))
    image_generation = types.KeyboardButton(_("🖼 Image generation"))
    instruction = types.KeyboardButton(_("📜 Instruction"))
    change_lang = types.KeyboardButton(_("🌏 Language"))
    if chat_id in ADMIN_ID:
        disable_btn = types.KeyboardButton(_("❌ Disable a bot"))
        kb.add(ask_question, detailed_answer, solving_tasks, image_generation, instruction, change_lang, disable_btn)
    else:
        feedback_btn = types.KeyboardButton(_("🗯 Feedback"))
        kb.add(ask_question, detailed_answer, solving_tasks, image_generation, instruction, change_lang, feedback_btn)
    return kb


def get_dialog_menu(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_new_dial = types.KeyboardButton(_("New dialogue"))
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(start_new_dial, main_menu)
    return kb


def get_main_menu_button(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(main_menu)
    return kb


def create_launch_menu(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_btn = types.KeyboardButton(_("▶ Launch"))
    kb.add(start_btn)
    return kb


def get_tasks_menu(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(main_menu)
    return kb


def get_image_mode_menu(_: Callable[[str], str]) -> ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    image_menu_button_512 = types.KeyboardButton("512x512")
    image_menu_button_1024 = types.KeyboardButton("1024x1024")
    main_menu = types.KeyboardButton(_("☰ Main menu"))
    kb.add(image_menu_button_512, image_menu_button_1024, main_menu)
    return kb
