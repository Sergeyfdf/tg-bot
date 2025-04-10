import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


# Вставь токен прямо в код
TOKEN = "7275976366:AAHKDh_lveIk6L3UtpJc33Wh89aU09-usFc"  # Замените на ваш токен бота

app = Flask(__name__)

# Функция, которая будет обрабатывать команду /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот.")

# Функция для обработки текстовых сообщений
async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

# Устанавливаем webhook
async def set_webhook():
    url = f"tg-bot-production-b3d7.up.railway.app/{TOKEN}"
    application = Application.builder().token(TOKEN).build()
    application.bot.set_webhook(url)

# Flask-обработчик для получения webhook запросов
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, application.bot)
    application.update_queue.put(update)  # Отправка запроса на обработку
    return "OK"

# Flask запуск
if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Настроить webhook
    set_webhook()

    # Запуск Flask-сервера
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
