import os
import sys
from pathlib import Path

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

required_vars = ["BOT_TOKEN", "ADMIN_ID", "DEALS_CHANNEL_ID"]
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    print(f"ERROR: Missing env: {', '.join(missing)}")
    sys.exit(1)

# Импортируем бота (предполагаем, что файл называется bot.py)
try:
    from bot import bot, dp, start_webhook
except ImportError:
    print("ERROR: Не удалось импортировать bot.py. Убедись, что файл переименован в bot.py и лежит в корне.")
    sys.exit(1)

if __name__ == "__main__":
    start_webhook()
