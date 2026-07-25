import os
import sys
import json
from pathlib import Path
from aiohttp import web
from aiogram.types import Update

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

# --- Попытка импорта bot.py с диагностикой ---
print("Текущая директория:", os.getcwd())
print("Файлы в корне:", os.listdir('.'))

try:
    from bot import bot, dp
    print("✅ Импорт из bot.py успешен (from bot import bot, dp)")
except ImportError as e:
    print(f"❌ Ошибка импорта через from bot: {e}")
    # Попробуем альтернативный способ
    try:
        import bot as bot_module
        bot = bot_module.bot
        dp = bot_module.dp
        print("✅ Импорт через import bot успешен")
    except ImportError as e2:
        print(f"❌ Не удалось импортировать bot ни одним способом: {e2}")
        print("Убедитесь, что файл называется ровно bot.py (регистр важен!)")
        sys.exit(1)

# --- Вебхук ---
WEBHOOK_PATH = "/webhook"
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")
if not BASE_URL:
    BASE_URL = "https://bto-garant.onrender.com"  # замените, если адрес другой
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update(**data)
        await dp.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return web.Response(status=500, text=str(e))

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    print("❌ Webhook удалён")

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Запуск сервера на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)
