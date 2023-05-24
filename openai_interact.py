import logging
import threading

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


class CompletionAI:
    """
    Represents an object of OpenAI of CompletionAI model.
    """
    url = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str, txt: str, max_tokens: int):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": txt}],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }

    def get_answer(self) -> str:
        json_response = None
        try:
            logging.info(
                f"{threading.current_thread().name} : отправка запроса, ключ: {self.api_key}, кол-во токенов: {self.data['max_tokens']}")
            start_time = datetime.now()
            logging.debug("Начало обработки запроса")
            json_response = requests.post(url=self.url, headers=self.headers, json=self.data).json()
            logging.info(f"Конец обработки запроса, длительность: {(datetime.now() - start_time).seconds} секунд")
            return json_response["choices"][0]["message"]["content"]
        except KeyError:
            logging.error("Возникла ошибка модели")
            raise OpenAIServerErrorException
        except Exception:
            if json_response["error"]["message"].startswith("This model's maximum context length is"):
                raise ExcessTokensException(
                    "Диалог получился слишком длинным. Необходимо нажать кнопку 'Начать новый диалог, чтобы избежать избытка токенов в запросе")
            # Dialog is too long. You need to press button "Start new dialogue" to avoid an excess of tokens


class ImageDALLEAI:
    """
    Represents an object of OpenAI of DALL-E model
    """
    url = "https://api.openai.com/v1/images/generations"

    def __init__(self, api_key: str, txt: str, size: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.data = {
            "prompt": txt,
            "n": 1,
            "size": size
        }
        logging.info(
            f"{threading.current_thread().name} : отправка запроса DALL-E, ключ: {api_key}")
        response = requests.post(url=self.url, headers=self.headers, json=self.data).json()
        self.img_url = response["data"][0]["url"]
        logging.info(
            f"{threading.current_thread().name} : получение изображения")


if __name__ == "__main__":
    ...
