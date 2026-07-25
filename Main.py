import os
import sys
import logging
from pathlib import Path
from aiohttp import web
from aiogram.types import Update

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("🚀 ЗАПУСК Main.py")

# Загрузка .env (если есть)
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
required = ["BOT_TOKEN", "ADMIN_ID", "DEALS_CHANNEL_ID"]
missing = [v for v in required if not os.environ.get(v)]
if missing:
    logger.error(f"❌ Не заданы переменные: {', '.join(missing)}")
    sys.exit(1)

# Импорт бота и диспетчера
try:
    from bot import bot, dp
    logger.info("✅ bot.py импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта bot.py: {e}")
    sys.exit(1)

# -------- НАСТРОЙКА ВЕБХУКА --------
WEBHOOK_PATH = "/webhook"
BASE_URL = "https://bto-garant.onrender.com"  # Правильный адрес
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"
logger.info(f"🔗 Вебхук будет установлен: {WEBHOOK_URL}")

async def handle_webhook(request):
    try:
        data = await request.json()
        logger.info("📩 Получен POST на /webhook")
        update = Update(**data)
        # В aiogram 3.x используется feed_update, а не process_update
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    except Exception as e:
        import traceback
        logger.error("❌ Ошибка при обработке webhook:")
        traceback.print_exc()
        return web.Response(status=500, text=str(e))

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)

async def on_startup(app):
    logger.info("🔄 Установка вебхука...")
    try:
        # Сброс старого вебхука и удаление ожидающих обновлений
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Старый вебхук удалён")
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"✅ Вебхук установлен: {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"❌ Не удалось установить вебхук: {e}")
        import traceback
        traceback.print_exc()

async def on_shutdown(app):
    await bot.delete_webhook()
    logger.info("✅ Вебхук удалён при остановке")

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Запуск сервера на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)
