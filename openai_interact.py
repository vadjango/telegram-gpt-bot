import logging

import requests
import json
from datetime import datetime


class ExcessTokensException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return f"ExcessTokenException has been raised"


class OpenAIServerErrorException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = 0

    def __str__(self):
        if self.message:
            return self.message
        else:
            return f"OpenAIServerErrorException has been raised"


class OpenAIAPIKey:
    """Represents the OpenAI API Key object, which has a value and amount of active requests"""

    __api_keys: list = []

    def __init__(self, value: str):
        self.__value = value
        self.__active_reqs_amount = 0

    def increment_active_reqs_amount(self):
        """Increase amount of active requests by 1"""
        self.__active_reqs_amount += 1

    def decrement_active_reqs_amount(self):
        """Decrease amount of active requests by 1"""
        self.__active_reqs_amount -= 1

    @property
    def value(self) -> str:
        """Property of the value of API key"""
        return self.__value

    def save_key(self) -> None:
        """Saves key to OpenAIAPIKey's list __api_keys"""
        self.__api_keys.append(self)

    def delete_key(self):
        self.__api_keys.remove(self)

    @property
    def active_reqs_amount(self):
        return self.__active_reqs_amount

    @staticmethod
    def get_all_keys():
        return OpenAIAPIKey.__api_keys


class CompletionAI:
    """
    Represents an object of OpenAI of CompletionAI model.
    """
    url = "https://api.openai.com/v1/completions"

    def __init__(self, api_key: OpenAIAPIKey, txt: str, max_tokens: int):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.value}"
        }
        self.data = {
            "model": "text-davinci-003",
            "prompt": txt,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }

    def get_answer(self) -> str:
        json_response = None
        try:
            start_time = datetime.now()
            logging.debug("Начало обработки запроса")
            json_response = requests.post(url=self.url, headers=self.headers, json=self.data).json()
            logging.info(f"Конец обработки запроса, длительность: {(datetime.now() - start_time).seconds} секунд")
            return json_response["choices"][0]["text"]
        except KeyError:
            if json_response["error"]["message"].startswith("This model's maximum context length is"):
                raise ExcessTokensException(
                    "Диалог получился слишком длинным. Необходимо нажать кнопку 'Начать новый диалог, чтобы избежать избытка токенов в запросе")
            elif json_response["error"]["message"] == \
                    'The server had an error while processing your request. Sorry about that!':
                logging.error("Возникла ошибка модели")
                raise OpenAIServerErrorException


if __name__ == "__main__":
    ok = OpenAIAPIKey("sadasd")
    ok.save_key()
    print("Called from class OpenAIAPIKey:", OpenAIAPIKey.get_all_keys())
    print("Called from instance OpenAIAPIKey:", ok.get_all_keys())
