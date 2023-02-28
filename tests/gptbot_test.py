import datetime
from unittest import TestCase, main
from telebot import types
from bot_users import USERS, User, UserMode
from main import send_request, bot_disabler
from openai_interact import *
from concurrent.futures import ThreadPoolExecutor

TEST_USER_ID = 975772882
USERS[TEST_USER_ID] = User(last_active_datetime=datetime.now(),
                           mode=None,
                           local="en_US",
                           has_active_request=False,
                           replicas="")
TEST_API_KEY = OpenAIAPIKey("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")
TEST_API_KEY.save_key()


class GPTBot(TestCase):

    def test_sending_dialogue_request(self):
        USERS[TEST_USER_ID]['mode'] = UserMode.DIALOG
        message = self.create_test_message("Привет, я ботяра")
        self.assertTrue(send_request(message, USERS[TEST_USER_ID]['mode']))

    def test_sending_detailed_answer_request(self):
        USERS[TEST_USER_ID]['mode'] = UserMode.DETAILED_ANSWER
        message = self.create_test_message("Привет, я ботяра")
        self.assertTrue(send_request(message, USERS[TEST_USER_ID]['mode']))

    def test_not_receiving_answer_after_dialog_mode_changing(self):
        """WARNING: for testing need to comment string 98 in main.py"""
        USERS[TEST_USER_ID]['mode'] = UserMode.DIALOG
        message = self.create_test_message("Привет, я ботяра.")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(send_request, message, USERS[TEST_USER_ID]['mode'])
            USERS[TEST_USER_ID]['mode'] = UserMode.DETAILED_ANSWER
            self.assertIsNone(future.result())

    def test_not_receiving_answer_after_detailed_answer_mode_changing(self):
        USERS[TEST_USER_ID]['mode'] = UserMode.DETAILED_ANSWER
        message = self.create_test_message("Привет, я ботяра.")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(send_request, message, USERS[TEST_USER_ID]['mode'])
            USERS[TEST_USER_ID]['mode'] = UserMode.DIALOG
            self.assertIsNone(future.result())


    @staticmethod
    def create_test_message(text):
        params = {"text": text}
        user = types.User(TEST_USER_ID, False, "TestBot")
        return types.Message(1, user, datetime.now(), user, "text", params, "")

    @staticmethod
    def create_callback_data(text):
        user = types.User(TEST_USER_ID, False, "TestBot")
        return types.CallbackQuery(id=1, from_user=user, data=text, chat_instance=975772882, json_string="")


if __name__ == "__main__":
    main()
