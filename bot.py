import json
import sqlite3
import re
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 🔑 Ключи API
TOKEN = "7275976366:AAHKDh_lveIk6L3UtpJc33Wh89aU09-usFc"
GROCLOUD_API_KEY = "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"
GROCLOUD_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
SEARCH_API_KEY = "AIzaSyAur8oQ3PhDcJlVfckw46d3bfAwmiNw6Q0"
SEARCH_ENGINE_ID = "77cd2223d2fe0432f"

# ✅ Разрешённый Telegram ID
ALLOWED_USER_ID = 2104542725  # ← замени на свой Telegram ID

# 📦 База данных SQLite
def init_db():
    conn = sqlite3.connect('user_history.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                        user_id INTEGER PRIMARY KEY,
                        history TEXT)''')
    conn.commit()
    conn.close()

def load_history(user_id):
    conn = sqlite3.connect('user_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT history FROM history WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    else:
        return [{"role": "system", "content": "Ты бот-помощник, отвечаешь коротко и понятно. Отвечаешь на русском."}]

def save_history(user_id, history):
    conn = sqlite3.connect('user_history.db')
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO history (user_id, history) VALUES (?, ?)", (user_id, json.dumps(history)))
    conn.commit()
    conn.close()

init_db()

# 🚀 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    context.user_data["history"] = load_history(user_id)
    await update.message.reply_text("Привет! Начинаем общение. Напиши что-нибудь.")

# 🔍 Проверка на ключевые слова для поиска
def is_search_request(text):
    keywords = ["найди", "поиск", "искать", "поищи", "интернет", "google"]
    return any(re.search(rf"\b{kw}\b", text.lower()) for kw in keywords)

# 🌐 Функция поиска в Google
async def search_internet(query):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": SEARCH_API_KEY,
        "cx": SEARCH_ENGINE_ID
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("items", [])
            return results
        except Exception as e:
            return f"Ошибка при запросе к Google: {e}"

# 🤖 Основная логика чата
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_id = update.message.from_user.id

    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    # Проверка на запрос поиска
    if is_search_request(user_input):
        results = await search_internet(user_input)
        if isinstance(results, str):  # Если ошибка
            await update.message.reply_text(results)
        else:
            result_text = "\n".join([f"{i+1}. {res['title']}: {res['link']}" for i, res in enumerate(results[:5])])
            await update.message.reply_text(f"Результаты поиска:\n{result_text}")
        return

    history = context.user_data.get("history", load_history(user_id))
    history.append({"role": "user", "content": user_input})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": history
    }
    headers = {
        "Authorization": f"Bearer {GROCLOUD_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GROCLOUD_ENDPOINT, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"].strip()
            history.append({"role": "assistant", "content": reply})
            save_history(user_id, history)
            context.user_data["history"] = history
            await update.message.reply_text(reply)
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")

# ▶️ Запуск бота
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
