from typing import Tuple, Any

import psycopg2
from psycopg2 import IntegrityError
import threading
from datetime import datetime
from config import *


# def get_user_loc(chat_id: int) -> str:
#     with psycopg2.connect(**DB_CONFIG) as conn:
#         cursor = conn.cursor()
#         cursor.execute(f"""SELECT locale
#                             FROM {TABLE_NAME}
#                             WHERE user_id = {chat_id}""")
#         return cursor.fetchone()[0]
#
#
# def init_user(chat_id: int):
#     """
#     Add a user to database if he doesn't exist (and also adds to USERS), otherwise just add to USERS
#     :param chat_id:
#     :return: None
#     """
#     thread_name = threading.current_thread().name
#     try:
#         with psycopg2.connect(**DB_CONFIG) as conn:
#             cursor = conn.cursor()
#             cursor.execute(f"""
#                             INSERT INTO {TABLE_NAME}
#                             VALUES (%s, %s, %s)""", (chat_id, "en_US", 0))
#             conn.commit()
#             logging.info(f"{thread_name} : добавлен юзер {chat_id} в таблицу")
#         USERS[chat_id] = UserInfo(last_active_datetime=datetime.now(),
#                                   has_active_request=False,
#                                   language="en_US",
#                                   mode=None,
#                                   replicas=None)
#     except IntegrityError:
#         USERS[chat_id] = UserInfo(last_active_datetime=datetime.now(),
#                                   has_active_request=False,
#                                   language=get_user_loc(chat_id=chat_id),
#                                   mode=None,
#                                   replicas=None)
#
#

def get_all_user_ids() -> tuple[int]:
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM {TABLE_NAME}")
        return tuple(map(lambda tup: tup[0], cursor.fetchall()))


def get_all_user_ids_and_languages():
    """
    Returns list of tuples of all user ids and languages from the database
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id, locale FROM {TABLE_NAME}")
        return cursor.fetchall()


def get_all_api_keys() -> tuple[str]:
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor: object = conn.cursor()
        cursor.execute("SELECT OPENAI_API_KEY FROM TELEGRAM_USERS_KEYS")
        return tuple(map(lambda tup: tup[0], cursor.fetchall()))


def add_user_to_database(chat_id) -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
                        INSERT INTO {TABLE_NAME}
                        VALUES (%s, %s, %s)""", (chat_id, "en_US", 0))
        conn.commit()


def delete_user_from_database(chat_id) -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
                        DELETE FROM test_telegram_users
                        WHERE user_id = %s
                        """, (chat_id,))
        conn.commit()


def get_user_loc(chat_id: int) -> str:
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT locale
                           FROM {TABLE_NAME}
                           WHERE user_id = {chat_id}""")
        return cursor.fetchone()[0]


if __name__ == "__main__":
    print(get_all_user_ids())
