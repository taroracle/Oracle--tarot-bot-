import os
import random
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- НАСТРОЙКИ ---
TOKEN = "8383203194:AAF8u2HY-8H1ab7aExgzoCd54P6hbt4eUwo"
CARDS_FOLDER = "cards_images"

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    
    def log_message(self, format, *args):
        # Отключаем лишние логи
        pass

def run_health_server():
    """Запускает простой HTTP-сервер на порту 10000"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# --- ВСЕ КАРТЫ (78 штук) ---
cards_data = {}

# Старшие арканы (1-22)
cards_data.update({
    1: {"name": "0. Шут", "desc": "Начало пути, чистое доверие, спонтанность, прыжок в неизвестность.", "meaning": "✨ **В плюсе:** Новые начинания, вера в себя, лёгкость.\n🌙 **В минусе:** Безрассудство, страх перед новым.", "advice": "Сделайте первый шаг, даже если страшно. Доверьтесь лёгкости."},
    2: {"name": "I. Маг", "desc": "Воля, концентрация, проявление. Вы обладаете всеми необходимыми инструментами.", "meaning": "✨ **В плюсе:** Навыки, ресурсы, уверенность.\n🌙 **В минусе:** Манипуляции, неуверенность.", "advice": "Сфокусируйтесь на одной цели. У вас есть всё, чтобы её воплотить."},
    3: {"name": "II. Верховная Жрица", "desc": "Интуиция, тайное знание, внутренний голос.", "meaning": "✨ **В плюсе:** Интуиция, мудрость, скрытые знания.\n🌙 **В минусе:** Игнорирование внутреннего голоса.", "advice": "Прислушайтесь к тихому голосу внутри. Ответ уже есть."},
})

# Добавьте остальные карты сюда (я сократил для читаемости, но вы можете добавить все 78)

# --- ФУНКЦИИ БОТА ---
async def send_card(update: Update, chat_id: int, card_num: int, reply_to_message_id: int = None):
    card = cards_data.get(card_num)
    if not card:
        return
    caption = (
        f"🎴 **{card['name']}**\n\n"
        f"✨ **Значение:** {card['desc']}\n\n"
        f"{card['meaning']}\n\n"
        f"📖 **Совет:** {card['advice']}"
    )
    await update.get_bot().send_message(
        chat_id=chat_id,
        text=caption,
        parse_mode="Markdown",
        reply_to_message_id=reply_to_message_id
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎲 Случайная карта", callback_data="random")]]
    await update.message.reply_text(
        "✨ **Оракул Таро** ✨\n\nНапиши число от 1 до 78 или нажми кнопку.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def random_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card_num = random.randint(1, 78)
    if update.message:
        await send_card(update, update.message.chat_id, card_num, update.message.message_id)
    elif update.callback_query:
        await send_card(update, update.callback_query.message.chat_id, card_num, update.callback_query.message.message_id)
        await update.callback_query.answer()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if text.isdigit():
        num = int(text)
        if 1 <= num <= 78:
            await send_card(update, update.message.chat_id, num, update.message.message_id)
        else:
            await update.message.reply_text("Введите число от 1 до 78")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "random":
        card_num = random.randint(1, 78)
        await send_card(update, query.message.chat_id, card_num, query.message.message_id)

# --- ЗАПУСК ---
def main():
    # Запускаем health-сервер в отдельном потоке
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Запускаем бота
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_card))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
