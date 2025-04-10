from flask import Flask, request
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# Инициализация Flask
app = Flask(__name__)

# Твой токен для бота
TOKEN = "7275976366:AAHKDh_lveIk6L3UtpJc33Wh89aU09-usFc"
bot = Bot(token=TOKEN)

# Устанавливаем Webhook
WEBHOOK_URL = "tg-bot-production-809d.up.railway.app/" + TOKEN  # Замените на свой URL на Railway

bot.set_webhook(url=WEBHOOK_URL)

# Обработчик команд
def start(update, context):
    update.message.reply_text("Привет! Я бот!")

def echo(update, context):
    update.message.reply_text(update.message.text)

# Инициализация Dispatcher
dispatcher = Dispatcher(bot, update_queue=None)

# Регистрируем обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text, echo))

# Главная страница для обработки webhook запросов
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    # Получаем обновление от Telegram
    update = request.get_json()
    dispatcher.process_update(update)
    return 'OK', 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
