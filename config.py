import os
import openai
from dotenv import load_dotenv

dotenv_path = "vars.env"
load_dotenv(dotenv_path)

TELEBOT_TOKEN = os.getenv("TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main":
    ...
