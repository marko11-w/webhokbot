import telebot
from flask import Flask, request
import threading
import time
import os
import json
from datetime import datetime
from telebot import types

TOKEN = "8116602303:AAHuS7IZt5jivjG68XL3AIVAasCpUcZRLic"
WEBHOOK_URL = "https://webhokbot-production-421f.up.railway.app/"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DATA_FILE = "data.json"
ADMINS = [7758666677]

# حفظ المستخدمين
def save_user(user_id):
    user_id = str(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({}, f)

        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        if user_id not in data:
            data[user_id] = now
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
    except Exception as e:
        print("خطأ في حفظ المستخدم:", e)

# إعداد webhook
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)

# الأزرار
def main_buttons(user_id):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons.row("💬 الدعم", "ℹ️ تعليمات")
    if user_id in ADMINS:
        buttons.row("📢 إرسال إعلان", "👥 عدد المستخدمين")
    return buttons

# بدء
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    save_user(user_id)
    bot.send_message(user_id,
        "👋 مرحبًا بك في البوت.\n\n"
        "✅ أرسل أي شيء أو اختر من القائمة:",
        reply_markup=main_buttons(user_id)
    )

# تعليمات
@bot.message_handler(func=lambda m: m.text == "ℹ️ تعليمات")
def show_help(message):
    bot.send_message(message.chat.id, "📌 تعليمات الاستخدام:\n- أرسل أي رسالة للتجربة.")

# دعم فني
@bot.message_handler(func=lambda m: m.text == "💬 الدعم")
def show_support(message):
    bot.send_message(message.chat.id, "💬 تواصل مع الدعم: @M_A_R_K75")

# عدد المستخدمين
@bot.message_handler(func=lambda m: m.text == "👥 عدد المستخدمين" and m.from_user.id in ADMINS)
def user_count(message):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        count = len(data)
        bot.send_message(message.chat.id, f"👥 عدد المستخدمين المسجلين: {count}")
    except:
        bot.send_message(message.chat.id, "❌ لا يمكن قراءة البيانات.")

# إرسال إعلان
@bot.message_handler(func=lambda m: m.text == "📢 إرسال إعلان" and m.from_user.id in ADMINS)
def ask_broadcast(message):
    msg = bot.send_message(message.chat.id, "📝 أرسل الآن نص الإعلان:")
    bot.register_next_step_handler(msg, broadcast_message)

def broadcast_message(message):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        success = 0
        fail = 0
        for uid in data:
            try:
                bot.send_message(uid, f"📢 إعلان:\n\n{message.text}")
                success += 1
                time.sleep(0.1)
            except:
                fail += 1
        bot.send_message(message.chat.id,
            f"✅ تم الإرسال إلى {success} مستخدم.\n"
            f"❌ فشل في الإرسال إلى {fail} مستخدم.")
    except:
        bot.send_message(message.chat.id, "❌ حدث خطأ أثناء الإرسال.")

# تشغيل السيرفر
def run():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run).start()
