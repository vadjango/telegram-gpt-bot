import datetime
from unittest import TestCase, main
from telebot import types
from bot_users import UserMode
from app import send_request, init_api_keys
from openai_interact import *
from concurrent.futures import ThreadPoolExecutor
from config import *
import requests
import time

TEST_USER_ID = 975772882


# TEST_API_KEY = "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"


def add_test_user_to_redis(id_):
    redis_.hset(f"user_{id_}", "local", "en_US")
    redis_.hset(f"user_{id_}", "has_active_request", 0)
    redis_.hset(f"user_{id_}", "replicas", "")


class GPTBot(TestCase):

    # def test_sending_dialogue_request(self):
    #     redis_.hset(f"user_{TEST_USER_ID}", "mode", UserMode.DIALOG.value)
    #     message = self.create_test_message("Привет, я ботяра")
    #     self.assertTrue(send_request(message))
    #
    # def test_sending_detailed_answer_request(self):
    #     redis_.hset(f"user_{TEST_USER_ID}", "mode", UserMode.DETAILED_ANSWER.value)
    #     message = self.create_test_message("Привет, я ботяра")
    #     self.assertTrue(send_request(message))
    #
    # def test_not_receiving_answer_after_dialog_mode_changing(self):
    #     """WARNING: for testing need to comment string 98 in main.py"""
    #     redis_.hset(f"user_{TEST_USER_ID}", "mode", UserMode.DIALOG.value)
    #     message = self.create_test_message("Привет, я ботяра.")
    #     with ThreadPoolExecutor(max_workers=1) as executor:
    #         future = executor.submit(send_request, message)
    #         time.sleep(0.3)
    #         redis_.hset(f"user_{TEST_USER_ID}", "mode", UserMode.DETAILED_ANSWER.value)
    #         self.assertIsNone(future.result())
    #
    # def test_not_receiving_answer_after_detailed_answer_mode_changing(self):
    #     """WARNING: for testing need to comment string 98 in main.py"""
    #     redis_.hset(f"user_{TEST_USER_ID}", "mode", UserMode.DETAILED_ANSWER.value)
    #     message = self.create_test_message("Привет, я ботяра.")
    #     with ThreadPoolExecutor(max_workers=1) as executor:
    #         future = executor.submit(send_request, message)
    #         time.sleep(0.5)
    #         redis_.hset(f"user_{TEST_USER_ID}", "mode", UserMode.DIALOG.value)
    #         self.assertIsNone(future.result())

    def test_no_mode_sending(self):
        redis_.flushdb()
        init_api_keys()
        message = self.create_test_message("Привет, я ботяра.")
        self.assertIsNone(send_request(message))

    @staticmethod
    def create_test_message(text: str) -> types.Message:
        params = {"text": text}
        user = types.User(TEST_USER_ID, False, "TestBot")
        return types.Message(1, user, datetime.now(), user, "text", params, "")

    @staticmethod
    def create_callback_data(text: str) -> types.CallbackQuery:
        user = types.User(TEST_USER_ID, False, "TestBot")
        return types.CallbackQuery(id=1, from_user=user, data=text, chat_instance=975772882, json_string="")


if __name__ == "__main__":
    init_api_keys()
    add_test_user_to_redis(TEST_USER_ID)
    main()
