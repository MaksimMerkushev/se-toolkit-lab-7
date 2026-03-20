import os
from dotenv import load_dotenv

# Подгружаем секреты из файла на уровень выше (из корня репозитория)
load_dotenv("../.env.bot.secret")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8650259454:AAE4eoQCtdS4VGxp7xwvLbLNICr6OsNRDIc")
LMS_API_URL = os.getenv("LMS_API_URL", "http://localhost:42002")
LMS_API_KEY = os.getenv("LMS_API_KEY", "my-secret-api-key")
LLM_API_KEY = os.getenv("LLM_API_KEY", "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")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
LLM_API_MODEL = os.getenv("LLM_API_MODEL", "google/gemini-3-flash-preview")
