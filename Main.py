import os
import sys
import json
import traceback
from pathlib import Path
from aiohttp import web
from aiogram.types import Update

# Загрузка .env (если есть)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    print("✅ Найден .env, загружаем...")
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

# Вывод всех переменных окружения (скрываем значения)
print("\n--- Содержимое os.environ (ключи) ---")
for key in os.environ.keys():
    if key in ("BOT_TOKEN", "ADMIN_ID", "DEALS_CHANNEL_ID", "PORT", "RENDER_EXTERNAL_URL"):
        print(f"{key} = установлена (значение скрыто)")
    else:
        print(f"{key} = установлена")

# Проверка конкретных переменных
for var in ["BOT_TOKEN", "ADMIN_ID", "DEALS_CHANNEL_ID"]:
    val = os.environ.get(var)
    if val is None:
        print(f"❌ Переменная {var} НЕ ЗАДАНА")
    else:
        print(f"✅ Переменная {var} задана (значение: {repr(val[:20])}...)")

# Проверка обязательных
required_vars = ["BOT_TOKEN", "ADMIN_ID", "DEALS_CHANNEL_ID"]
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    print(f"ERROR: Missing env: {', '.join(missing)}")
    sys.exit(1)

# --- Импорт bot.py с полной диагностикой ---
print("\n--- Импорт bot.py ---")
try:
    import bot
    print("Модуль bot загружен")
    if hasattr(bot, 'bot'):
        bot_obj = bot.bot
        print("Объект bot найден")
    else:
        print("❌ в модуле bot нет атрибута bot")
        print("Атрибуты модуля:", dir(bot))
        sys.exit(1)
    if hasattr(bot, 'dp'):
        dp_obj = bot.dp
        print("Объект dp найден")
    else:
        print("❌ в модуле bot нет атрибута dp")
        sys.exit(1)
except Exception as e:
    print("❌ Ошибка при импорте bot.py:")
    traceback.print_exc()
    sys.exit(1)

# --- Вебхук ---
WEBHOOK_PATH = "/webhook"
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")
if not BASE_URL:
    BASE_URL = "https://bto-garant.onrender.com"  # замените на свой адрес
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update(**data)
        await dp_obj.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return web.Response(status=500, text=str(e))

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)

async def on_startup(app):
    await bot_obj.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot_obj.delete_webhook()
    print("❌ Webhook удалён")

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Запуск сервера на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)
