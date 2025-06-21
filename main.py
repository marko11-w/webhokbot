import telebot
from flask import Flask, request
import threading
import schedule
import time
import os

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# قاعدة بيانات وهمية - للتجربة فقط
users_data = {
    str(ADMIN_ID): {"balance": 0, "confirmed": True}
}

def save_data():
    pass  # يمكن ربطها بـ JSON أو Google Sheets لاحقًا

def send_daily_profits():
    for uid, user in users_data.items():
        if user.get("confirmed"):
            daily = 15000
            user['balance'] += daily
            try:
                bot.send_message(int(uid), f"💸 أرباح اليوم: {daily} دينار\n📊 رصيدك: {user['balance']} دينار")
            except:
                continue
    save_data()

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_data:
        users_data[uid] = {"balance": 0, "confirmed": False}
    status = "✅ مفعل" if users_data[uid]["confirmed"] else "❌ غير مفعل"
    bot.reply_to(message, f"👋 مرحباً بك!\n📊 رصيدك: {users_data[uid]['balance']} دينار\n🔐 حالتك: {status}")

@bot.message_handler(commands=['balance'])
def balance(message):
    uid = str(message.from_user.id)
    if uid not in users_data:
        bot.reply_to(message, "❌ أنت غير مشترك.")
        return
    bot.reply_to(message, f"📊 رصيدك: {users_data[uid]['balance']} دينار")

@bot.message_handler(commands=['confirm'])
def confirm_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = message.text.split()[1]
        if uid in users_data:
            users_data[uid]['confirmed'] = True
            bot.reply_to(message, f"✅ تم تفعيل المستخدم {uid}")
        else:
            bot.reply_to(message, "❌ المستخدم غير موجود")
    except:
        bot.reply_to(message, "❌ استخدم الأمر هكذا: /confirm <user_id>")

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = "👥 قائمة المستخدمين:\n"
    for uid, data in users_data.items():
        status = "✅" if data["confirmed"] else "❌"
        msg += f"{uid} - {status} - {data['balance']} دينار\n"
    bot.reply_to(message, msg)

@bot.message_handler(commands=['sendprofits'])
def manual_send(message):
    if message.from_user.id != ADMIN_ID:
        return
    send_daily_profits()
    bot.send_message(ADMIN_ID, "✅ تم إرسال الأرباح يدوياً.")

schedule.every(24).hours.do(send_daily_profits)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(10)

@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return '', 200

if __name__ == "__main__":
    threading.Thread(target=run_schedule).start()
    app.run(host="0.0.0.0", port=8080)
