import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask, request
import json
import os

TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
ADMIN_ID = 7758666677
DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# تحميل أو إنشاء ملف البيانات
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": {},  # user_id: { "active": bool }
        }, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_subscribed(user_id):
    data = load_data()
    user_str = str(user_id)
    return data["users"].get(user_str, {}).get("active", False)

def set_subscription(user_id, status: bool):
    data = load_data()
    user_str = str(user_id)
    if user_str not in data["users"]:
        data["users"][user_str] = {}
    data["users"][user_str]["active"] = status
    save_data(data)

# رسالة ثابتة لجميع المستخدمين
def send_contact_admin_message(chat_id):
    bot.send_message(chat_id, "عليك مراسلة الأدمن لتفعيل الاشتراك في البوت.")

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    # سجّل المستخدم في data.json لو مش موجود
    data = load_data()
    user_str = str(user_id)
    if user_str not in data["users"]:
        data["users"][user_str] = {"active": False}
        save_data(data)
    send_contact_admin_message(user_id)

@bot.message_handler(func=lambda m: True)
def all_messages_handler(message):
    send_contact_admin_message(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def all_callback_handler(call):
    send_contact_admin_message(call.from_user.id)
    bot.answer_callback_query(call.id)

# أوامر الأدمن لتفعيل/تعطيل الاشتراك فقط
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text)
def admin_commands(message):
    text = message.text.strip()
    if text.startswith("/activate"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            target_id = parts[1]
            set_subscription(target_id, True)
            bot.send_message(ADMIN_ID, f"تم تفعيل الاشتراك للمستخدم {target_id}")
            bot.send_message(int(target_id), "🎉 تم تفعيل اشتراكك في البوت، يمكنك الآن استخدامه.")
        else:
            bot.send_message(ADMIN_ID, "استخدام: /activate user_id")
    elif text.startswith("/deactivate"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            target_id = parts[1]
            set_subscription(target_id, False)
            bot.send_message(ADMIN_ID, f"تم تعطيل الاشتراك للمستخدم {target_id}")
            bot.send_message(int(target_id), "⚠️ تم تعطيل اشتراكك في البوت.")
        else:
            bot.send_message(ADMIN_ID, "استخدام: /deactivate user_id")
    elif text == "/list":
        data = load_data()
        users = [f"{uid} - {'مفعل' if info.get('active', False) else 'معطل'}" for uid, info in data["users"].items()]
        msg = "قائمة المستخدمين:\n" + "\n".join(users)
        bot.send_message(ADMIN_ID, msg)

# Flask ويب هوك
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK"

bot.remove_webhook()
WEBHOOK_URL = "https://webhokbot-bothack.up.railway.app/" + TOKEN  # عدل إلى رابط مشروعك
bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
