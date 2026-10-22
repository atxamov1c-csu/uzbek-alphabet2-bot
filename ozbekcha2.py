from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sqlite3
import threading
import time
import urllib.request
import telebot

TOKEN = "8998834423:AAFxxRncTDS3aW0Y7xSLBKPnpxsQTF52-r4"
ADMIN_ID = 1281646026

bot = telebot.TeleBot(TOKEN)
DB_PATH = "bot_users.db"


# --- ИНИЦИАЛИЗАЦИЯ И РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
  with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_seen TIMESTAMP
            )
        """)
    conn.commit()


def log_user(user):
  """Сохраняет пользователя или обновляет время его последнего действия."""
  try:
    with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO users (user_id, username, first_name, last_seen)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_seen=excluded.last_seen
            """,
          (
              user.id,
              user.username or "No username",
              user.first_name or "",
              datetime.now(),
          ),
      )
      conn.commit()
  except Exception as e:
    print(f"Ошибка БД: {e}")


def get_analytics():
  """Считает активность пользователей за день, неделю, месяц."""
  now = datetime.now()
  day_ago = now - timedelta(days=1)
  week_ago = now - timedelta(days=7)
  month_ago = now - timedelta(days=30)

  with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (day_ago,))
    daily_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE last_seen >= ?", (week_ago,)
    )
    weekly_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE last_seen >= ?", (month_ago,)
    )
    monthly_users = cursor.fetchone()[0]

  text = "📊 **Статистика бота:**\n\n"
  text += f"👥 Всего пользователей: **{total_users}**\n"
  text += f"📅 За последние 24 часа: **{daily_users}**\n"
  text += f"🗓 За последние 7 дней: **{weekly_users}**\n"
  text += f"📆 За последние 30 дней: **{monthly_users}**\n\n"
  text += "📄 Полный список всех пользователей прикреплён файлом ниже."
  return text


def generate_users_file():
  """Создает текстовый файл со всеми пользователями."""
  filename = "users_list.txt"
  with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, first_name, last_seen FROM users ORDER BY"
        " last_seen DESC"
    )
    rows = cursor.fetchall()

  with open(filename, "w", encoding="utf-8") as f:
    f.write(f"СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ БОТА (Всего: {len(rows)})\n")
    f.write(
        f"Выгружено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    f.write("=" * 65 + "\n\n")

    for idx, (u_id, u_name, f_name, l_seen) in enumerate(rows, 1):
      seen_time = l_seen.split(".")[0]
      uname_str = f"@{u_name}" if u_name != "No username" else "Нет никнейма"
      f.write(
          f"{idx}. ID: {u_id} | Юзернейм: {uname_str} | Имя: {f_name} | Был"
          f" в сети: {seen_time}\n"
      )

  return filename


# --- ЛОГИКА ТРАНСЛИТЕРАЦИИ ---
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


# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---
@bot.message_handler(commands=["stats"])
def show_stats(message):
  if message.from_user.id != ADMIN_ID:
    return

  # 1. Отправляем текстовую статистику
  stats_message = get_analytics()
  bot.reply_to(message, stats_message, parse_mode="Markdown")

  # 2. Генерируем и отправляем .txt файл со всеми пользователями
  filepath = generate_users_file()
  with open(filepath, "rb") as f:
    bot.send_document(
        message.chat.id, f, caption="📁 База всех пользователей бота"
    )

  # Удаляем временный файл с диска после отправки
  if os.path.exists(filepath):
    os.remove(filepath)


@bot.message_handler(commands=["start"])
def send_welcome(message):
  log_user(message.from_user)
  bot.reply_to(
      message,
      "Assalomu alaykum! Menga matn yuboring, men uni yangi o'zbek alifbosiga"
      " o'tkazib beraman (Ŏ, Ğ, Ş, Ç).",
  )


@bot.message_handler(func=lambda message: True)
def translate_text(message):
  log_user(message.from_user)
  original_text = message.text
  converted_text = convert_to_new_alphabet(original_text)
  bot.reply_to(message, converted_text)


# --- СЕРВЕР ДЛЯ RENDER И АНТИ-ЗАСЫПАНИЕ ---
class SimpleHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"OK")

  def log_message(self, format, *args):
    return


def run_web():
  port = int(os.environ.get("PORT", 8080))
  server = HTTPServer(("0.0.0.0", port), SimpleHandler)
  server.serve_forever()


def keep_alive():
  time.sleep(30)
  port = os.environ.get("PORT", "8080")
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
    time.sleep(600)


# Запуск компонентов
init_db()
threading.Thread(target=run_web, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()

print("Бот запущен, логирование в файл готово...")
bot.infinity_polling()