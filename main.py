import subprocess
import sys

# دالة لتثبيت مكتبة إذا غير موجودة
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# تثبيت المكتبات المطلوبة
install_package('telebot')
install_package('requests')

import telebot
import requests
import time
import itertools

# توكن البوت الخاص بك
BOT_TOKEN = "7504294266:AAHgYMIxq5G1hxXRmGF2O7zYKKi-bPjReeM"
bot = telebot.TeleBot(BOT_TOKEN)

SAVE_FILE = "available.txt"

def is_available(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.status_code == 404

def generate_three_char_usernames():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    for combo in itertools.product(chars, repeat=3):
        yield ''.join(combo)

def start_search(chat_id):
    total_checked = 0
    found_available = 0

    for username in generate_three_char_usernames():
        total_checked += 1

        if is_available(username):
            found_available += 1
            bot.send_message(chat_id, f"✅ Available username found: @{username}")
            with open(SAVE_FILE, "a") as file:
                file.write(username + "\n")
            return

        if total_checked % 100 == 0:
            bot.send_message(chat_id, f"📊 Checked: {total_checked} usernames\n✅ Found available: {found_available}")

        time.sleep(1)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "🔍 Starting search for a 3-character Instagram username (letters + digits)...")
    start_search(message.chat.id)

bot.polling()
