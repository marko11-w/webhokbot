import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import json
import os
import time

API_TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
CHANNEL_USERNAME = "MARK01i"
ADMIN_ID = 7758666677
DATA_FILE = "data.json"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# تأكد من وجود ملف البيانات
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": []}, f)

def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

def send_subscription_prompt(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME}"))
    bot.send_message(chat_id, "📛 يجب عليك الاشتراك في القناة أولاً لاستخدام هذا البوت.", reply_markup=keyboard)

@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    data = load_users()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_users(data)
        bot.send_message(ADMIN_ID, f"🔔 مستخدم جديد بدأ البوت: @{message.from_user.username or 'لا يوجد'} - {user_id}")

    if not is_subscribed(user_id):
        send_subscription_prompt(user_id)
        return

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📘 اختراق فيسبوك", callback_data="hack_facebook"))
    keyboard.add(InlineKeyboardButton("📷 اختراق انستقرام", callback_data="hack_instagram"))
    keyboard.add(InlineKeyboardButton("🎥 اختراق تيك توك", callback_data="hack_tiktok"))
    keyboard.add(InlineKeyboardButton("📶 اختراق شبكات WiFi", callback_data="hack_wifi"))
    bot.send_message(user_id, "🎯 اختر نوع الخدمة:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if not is_subscribed(user_id):
        send_subscription_prompt(user_id)
        return

    label = call.data.replace("hack_", "").capitalize()
    msg = bot.send_message(call.message.chat.id, f"📥 أرسل رابط الحساب أو رقم الهاتف لبدء عملية {label}:")
    bot.register_next_step_handler(msg, process_target, label)

def process_target(message, label):
    chat_id = message.chat.id

    loading_msgs = [
        "🔍 جاري تحليل الهدف...",
        "📡 الاتصال بالخوادم...",
        "🧠 تفعيل الذكاء الاصطناعي...",
        "🔓 فك التشفير...",
        "📂 استخراج البيانات...",
    ]

    sent_msg = bot.send_message(chat_id, loading_msgs[0])
    time.sleep(1.5)

    for percent in [15, 33, 58, 76, 100]:
        try:
            bot.edit_message_text(f"🔄 جاري تنفيذ العملية... {percent}%", chat_id, sent_msg.message_id)
        except:
            pass
        time.sleep(1.3)

    for msg in loading_msgs[1:]:
        bot.send_message(chat_id, msg)
        time.sleep(1.8)

    password = f"pass_{str(message.from_user.id)[-3:]}_{label[:3]}"
    bot.send_message(chat_id, f"✅ كلمة السر المحتملة: {password}")
    bot.send_message(chat_id, f"✅ تم تنفيذ العملية بنجاح.")

# Webhook endpoints
@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

bot.remove_webhook()
bot.set_webhook(url=f"https://charhbot-production.up.railway.app/{API_TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
