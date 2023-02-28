from typing import TypedDict, Optional, Union
from datetime import datetime
from enum import Enum


class UserMode(Enum):
    """Enumeration, which consists of two user modes: DIALOG and DETAILED_ANSWER"""
    DIALOG = "dialog"
    DETAILED_ANSWER = "detailed_answer"


class User(TypedDict):
    last_active_datetime: datetime
    mode: Optional[UserMode]
    local: str
    has_active_request: bool
    replicas: str


class LocaleDoesNotSupportException(Exception):
    pass


class NotStringReplicasException(Exception):
    pass


USERS: dict[int, User] = {}


def add_user(user_id, local="en_US"):
    USERS[user_id] = User(last_active_datetime=datetime.now(),
                          has_active_request=False,
                          local=local,
                          mode=None,
                          replicas="")


