from enum import Enum


class UserMode(Enum):
    """Enumeration, which consists of two user modes: DIALOG and DETAILED_ANSWER"""
    DIALOG = "dialog"
    DETAILED_ANSWER = "detailed_answer"
    SOLVING_TASKS = "solving_tasks"
    IMAGE_GENERATION = "image_generation"


if __name__ == "__main__":
    pass
