from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading
import telebot

TOKEN = "8998834423:AAEl1eJ1P578ckeaYztlnGdwM4KocUklngM"
bot = telebot.TeleBot(TOKEN)


def convert_to_new_alphabet(text):
  replacements = {
      "Sh": "Ş",
      "sh": "ş",
      "SH": "Ş",
      "Ch": "Ç",
      "ch": "ç",
      "CH": "Ç",
      "Ng": "Ŋ",
      "ng": "ŋ",
      "NG": "Ŋ",
      "O‘": "Ŏ",
      "o‘": "ŏ",
      "O'": "Ŏ",
      "o'": "ŏ",
      "Oʻ": "Ŏ",
      "oʻ": "ŏ",
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
      " o'tkazib beraman (Ŏ, Ğ, Ş, Ç, Ŋ).",
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


threading.Thread(target=run_web, daemon=True).start()

print("Бот запущен и ожидает сообщения...")
bot.infinity_polling()