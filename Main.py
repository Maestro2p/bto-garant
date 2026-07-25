import os
import sys
import logging
from pathlib import Path
from aiohttp import web
from aiogram.types import Update

print("🚀 Запуск Main.py")

# Загрузка .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    print("📂 Найден .env, загружаем...")
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if not os.environ.get(key):
                    os.environ[key] = value
                    print(f"   Загружено из .env: {key}=***")
else:
    print("ℹ️ .env не найден, используем переменные окружения Render")

# Проверка переменных
required_vars = ["BOT_TOKEN", "ADMIN_ID", "DEALS_CHANNEL_ID"]
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    print(f"❌ ОШИБКА: не заданы переменные: {', '.join(missing)}")
    sys.exit(1)
else:
    print("✅ Все переменные окружения заданы")

# Импортируем бота и диспетчер из bot.py
try:
    from bot import bot, dp
    print("✅ bot.py импортирован успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта bot.py: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WEBHOOK_PATH = "/webhook"
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")
if not BASE_URL:
    BASE_URL = "https://bto-garant.onrender.com"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"
print(f"🔗 Будет установлен вебхук: {WEBHOOK_URL}")

async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 Получен POST на /webhook: {data}")
        update = Update(**data)
        await dp.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        import traceback
        print("❌ Ошибка при обработке webhook:")
        traceback.print_exc()
        return web.Response(status=500, text=f"Error: {str(e)}")

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)

async def on_startup(app):
    print("🔄 Установка вебхука...")
    try:
        await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook установлен: {WEBHOOK_URL}")
    except Exception as e:
        print(f"❌ Не удалось установить вебхук: {e}")
        import traceback
        traceback.print_exc()

async def on_shutdown(app):
    print("🔄 Удаление вебхука...")
    try:
        await bot.delete_webhook()
        print("✅ Webhook удалён")
    except Exception as e:
        print(f"❌ Ошибка удаления вебхука: {e}")

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Запуск сервера на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)
