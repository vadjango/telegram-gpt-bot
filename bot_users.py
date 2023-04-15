from enum import Enum


class UserMode(Enum):
    """Enumeration, which consists of two user modes: DIALOG and DETAILED_ANSWER"""
    DIALOG = "dialog"
    DETAILED_ANSWER = "detailed_answer"
    SOLVING_TASKS = "solving_tasks"



