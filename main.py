import telebot
from flask import Flask, request
import threading
import schedule
import time

API_TOKEN = '7877754239:AAFP3ljogZijfNia3sVdgnEaIPR9EbrgGK8'
ADMIN_ID = 7758666677

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# قاعدة بيانات وهمية للمستخدمين
users_data = {
    "7758666677": {"balance": 50000, "confirmed": True}
}

def save_data():
    pass  # يمكن ربطها بملف أو Google Sheets لاحقًا

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

@bot.message_handler(commands=['sendprofits'])
def manual_send(message):
    if message.from_user.id != ADMIN_ID:
        return
    send_daily_profits()
    bot.send_message(ADMIN_ID, "✅ تم إرسال الأرباح يدوياً.")

# جدولة الأرباح اليومية
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