import os
import sys
from pathlib import Path
from aiohttp import web
from aiogram.webhook import webhook_app

# Загрузка .env (для локального теста)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if not os.environ.get(key):
                    os.environ[key] = value

# Проверка переменных окружения
required_vars = ["BOT_TOKEN", "ADMIN_ID", "DEALS_CHANNEL_ID"]
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    print(f"ERROR: Missing env: {', '.join(missing)}")
    sys.exit(1)

# Импортируем бота и диспетчер из bot.py
try:
    from bot import bot, dp
except ImportError:
    print("ERROR: Не удалось импортировать bot.py. Убедись, что файл bot.py лежит в корне.")
    sys.exit(1)

WEBHOOK_PATH = "/webhook"
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")
if not BASE_URL:
    BASE_URL = "https://bto-garant.onrender.com"  # замените, если адрес другой
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    print("Webhook удалён")

def start_webhook():
    app = webhook_app(dp, bot, webhook_path=WEBHOOK_PATH)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    port = int(os.environ.get("PORT", 8080))
    print(f"Запуск aiohttp сервера на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    start_webhook()
