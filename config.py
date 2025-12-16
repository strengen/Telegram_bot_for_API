import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Failed loading environment variables")
else:
    load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
DB_PATH = os.getenv("DB_PATH")

