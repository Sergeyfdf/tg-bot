from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = "7275976366:AAHKDh_lveIk6L3UtpJc33Wh89aU09-usFc"  # 🔁 вставь свой токен сюда
WEBHOOK_URL = "https://tg-bot-production-809d.up.railway.app"

app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я работаю через webhook!")

# Ответ на любое текстовое сообщение
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты сказал: {update.message.text}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Входящий webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok"

# Проверочная страница
@app.route("/")
def index():
    return "Бот работает! 🎉"

# Установка webhook при старте
async def setup_webhook():
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    print("Webhook установлен")

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_webhook())
    app.run(host="0.0.0.0", port=8080)
