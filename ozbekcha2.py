import telebot

# Токен твоего бота: @ozbekca2_bot
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
  print(
      f"Получена команда /start от пользователя: {message.from_user.first_name}"
  )
  bot.reply_to(
      message,
      "Assalomu alaykum! Menga matn yuboring, men uni yangi o'zbek alifbosiga"
      " o'tkazib beraman (Ŏ, Ğ, Ş, Ç, Ŋ).",
  )


@bot.message_handler(func=lambda message: True)
def translate_text(message):
  print(
      f"Получено сообщение от {message.from_user.first_name}: {message.text}"
  )
  original_text = message.text
  converted_text = convert_to_new_alphabet(original_text)
  bot.reply_to(message, converted_text)


print("Бот запущен и ожидает сообщения...")
bot.infinity_polling()