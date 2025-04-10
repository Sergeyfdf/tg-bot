import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

app = Flask(__name__)

# Вводим свой токен
TELEGRAM_TOKEN = '7275976366:AAHKDh_lveIk6L3UtpJc33Wh89aU09-usFc'

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет, я твой бот!')

# Основная функция для обработки сообщений
async def echo(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(update.message.text)

# Настройка webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_str = request.get_data().decode("UTF-8")
        update = Update.de_json(json_str)
        application.update_queue.put(update)  # передаем обновление в очередь
        return "OK!"

# Настройка бота
async def set_webhook():
    url = f"https://tg-bot-production-809d.up.railway.app/webhook"
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    await application.bot.set_webhook(url)  # используем await для set_webhook
    return application

# Настройка диспетчера
async def main():
    application = await set_webhook()  # вызываем асинхронную функцию для установки webhook
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запуск приложения на Flask
    app.run(host="0.0.0.0", port=8080)

if __name__ == '__main__':
    asyncio.run(main())
