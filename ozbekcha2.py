from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading
import time
import urllib.request
import telebot

TOKEN = "8998834423:AAFxxRncTDS3aW0Y7xSLBKPnpxsQTF52-r4"
bot = telebot.TeleBot(TOKEN)


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
      "Assalomu alaykum! Menga matn yuboring, men uni yangi o'zbek alifbosiga"
      " o'tkazib beraman (Ŏ, Ğ, Ş, Ç).",
  )


@bot.message_handler(func=lambda message: True)
def translate_text(message):
  original_text = message.text
  converted_text = convert_to_new_alphabet(original_text)
  bot.reply_to(message, converted_text)


# Простой веб-сервер для Render
class SimpleHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"OK")

  def log_message(self, format, *args):
    return  # Не засоряем логи Render постоянными отчетами пинга


def run_web():
  port = int(os.environ.get("PORT", 8080))
  server = HTTPServer(("0.0.0.0", port), SimpleHandler)
  server.serve_forever()


# Функция защиты от сна: пингует сервис каждые 10 минут
def keep_alive():
  time.sleep(30)
  port = os.environ.get("PORT", "8080")
  # Берем публичный адрес Render или стучимся в локальный порт
  external_url = os.environ.get("RENDER_EXTERNAL_URL")
  target_url = (
      external_url if external_url else f"http://127.0.0.1:{port}/"
  )

  while True:
    try:
      req = urllib.request.Request(
          target_url, headers={"User-Agent": "Render-KeepAlive"}
      )
      with urllib.request.urlopen(req, timeout=10):
        pass
    except Exception:
      pass
    time.sleep(600)  # Спим 10 минут (таймаут засыпания Render — 15 минут)


# Запуск сервера и анти-сна в фоновых потоках
threading.Thread(target=run_web, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()

print("Бот запущен и защищен от засыпания...")
bot.infinity_polling()