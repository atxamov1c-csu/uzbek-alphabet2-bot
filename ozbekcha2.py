import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot

TOKEN = "8998834423:AAFxxRncTDS3aW0Y7xSLBKPnpxsQTF52-r4"
bot = telebot.TeleBot(TOKEN)

# Вставь сюда свой URL из Render
RENDER_URL = "https://твой-проект.onrender.com"


def convert_to_new_alphabet(text):
    replacements = {
        "Sh": "Ş",
        "sh": "ş",
        "SH": "Ş",
        "Ch": "Ç",
        "ch": "ç",
        "CH": "Ç",
        "O‘": "Ö",
        "o‘": "ö",
        "O'": "Ö",
        "o'": "ö",
        "Oʻ": "Ö",
        "oʻ": "ö",
        "G‘": "Ğ",
        "g‘": "ğ",
        "G'": "Ğ",
        "g'": "ğ",
        "Gʻ": "Ğ",
        "gʻ": "ğ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Assalomu alaykum! Menga matn yuboring, men uni yangi o'zbek alifbosiga o'tkazib beraman (Ŏ, Ğ, Ş, Ç).",
    )


@bot.message_handler(func=lambda message: True)
def translate_text(message):
    original_text = message.text
    converted_text = convert_to_new_alphabet(original_text)
    bot.reply_to(message, converted_text)


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")


def run_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()


def keep_alive():
    time.sleep(30)  # Пауза 30 сек после старта, чтобы сервер успел подняться
    while True:
        try:
            if "onrender.com" in RENDER_URL:
                req = urllib.request.Request(
                    RENDER_URL,
                    headers={"User-Agent": "Render-KeepAlive-Bot"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    print(f"[Keep-Alive] Ping успешен, статус: {response.status}")
        except Exception as e:
            print(f"[Keep-Alive] Ошибка пинга: {e}")
        time.sleep(600)  # Пинг каждые 10 минут (до 15-минутного таймаута)


# Запуск веб-сервера для Render
threading.Thread(target=run_web, daemon=True).start()

# Запуск самопинга против засыпания
threading.Thread(target=keep_alive, daemon=True).start()

print("Бот запущен и ожидает сообщения...")
bot.infinity_polling()