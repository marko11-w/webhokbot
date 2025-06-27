import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import json
import os

TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
ADMIN_ID = 7758666677
ADMIN_USERNAME = "@M_A_R_K75"
DATA_FILE = "users.json"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"approved": []}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def is_approved(user_id):
    data = load_data()
    return user_id in data["approved"]

def notify_admin(user):
    try:
        bot.send_message(ADMIN_ID, f"🆕 مستخدم جديد دخل البوت:\n\n🧑‍💻 الاسم: {user.first_name}\n🆔 الآيدي: {user.id}\n🔗 يوزر: @{user.username if user.username else 'لا يوجد'}")
    except:
        pass

@bot.message_handler(commands=["approve"])
def approve_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.split()[1])
        data = load_data()
        if uid not in data["approved"]:
            data["approved"].append(uid)
            save_data(data)
            bot.send_message(uid, "✅ تم تفعيل اشتراكك من قبل الإدارة. يمكنك استخدام البوت الآن.")
            bot.send_message(message.chat.id, "✅ تم تفعيل المستخدم.")
        else:
            bot.send_message(message.chat.id, "🚫 المستخدم مفعل مسبقًا.")
    except:
        bot.send_message(message.chat.id, "❌ تأكد من كتابة الأمر هكذا:\n/approve 123456789")

@bot.message_handler(commands=["reject"])
def reject_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.split()[1])
        data = load_data()
        if uid in data["approved"]:
            data["approved"].remove(uid)
            save_data(data)
            bot.send_message(uid, "🚫 تم رفض اشتراكك من قبل الإدارة.")
            bot.send_message(message.chat.id, "✅ تم حذف المستخدم.")
        else:
            bot.send_message(message.chat.id, "🚫 المستخدم غير موجود.")
    except:
        bot.send_message(message.chat.id, "❌ تأكد من كتابة الأمر هكذا:\n/reject 123456789")

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    if not is_approved(user_id):
        notify_admin(message.from_user)
        bot.send_message(user_id, f"🚫 عليك مراسلة الأدمن لتفعيل الاشتراك:\n{ADMIN_USERNAME}\n💸 سعر الاشتراك: 25 ألف دينار")
        return
    bot.send_message(user_id, "✅ تم تفعيلك مسبقًا، ولكن لا توجد أوامر مفعلة بعد.")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running."

bot.remove_webhook()
bot.set_webhook(url="https://webhokbot-bothack.up.railway.app/" + TOKEN)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
