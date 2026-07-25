# Удали это:
# if __name__ == "__main__":
#     asyncio.run(main())

# Добавь это (в самый конец файла):
async def set_webhook(bot: Bot, webhook_url: str):
    await bot.set_webhook(webhook_url)

def start_webhook():
    import uvicorn
    from aiogram.webhook import webhook_app

    WEBHOOK_PATH = "/webhook"
    BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if not BASE_URL:
        BASE_URL = "https://bto-garant.onrender.com"  # твой адрес
    WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

    app = webhook_app(dp, bot, webhook_path=WEBHOOK_PATH)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
