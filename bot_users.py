from typing import TypedDict, Optional
from datetime import datetime
from enum import Enum


class UserMode(Enum):
    DIALOG = "dialog"
    DETAILED_ANSWER = "detailed_answer"


class UserInfo(TypedDict):
    last_active_datetime: datetime
    mode: UserMode
    has_active_request: bool
    replicas: str


if __name__ == "__main__":
    ...
