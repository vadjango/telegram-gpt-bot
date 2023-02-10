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


class CompletionAI:
    url = "https://api.openai.com/v1/completions"

    def __init__(self, api_key, txt, max_tokens):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.data = {
            "model": "text-davinci-003",
            "prompt": txt,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        print(f"Message: {txt}")

    def get_answer(self) -> str:
        obj = None
        while True:
            try:
                start_time = datetime.now()
                print("Начало обработки запроса")
                obj = requests.post(url=self.url, headers=self.headers, json=self.data).json()
                print(f"Конец обработки запроса, длительность: {(datetime.now() - start_time).seconds} секунд")
                return obj["choices"][0]["text"]
            except KeyError:
                if obj["error"]["message"].startswith("This model's maximum context length is"):
                    raise ExcessTokensException(
                        "Диалог получился слишком длинным. Необходимо нажать кнопку 'Начать новый диалог, чтобы избежать избытка токенов в запросе")
                elif obj["error"][
                    "message"] == 'The server had an error while processing your request. Sorry about that!':
                    print("Возникла ошибка модели")
                    obj = json.loads(requests.post(url=self.url, headers=self.headers, json=self.data).text)
