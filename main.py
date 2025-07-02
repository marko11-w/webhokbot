import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import json
import os
import requests

TOKEN = "8116602303:AAHuS7IZt5jivjG68XL3AIVAasCpUcZRLic"
CHANNEL_ID = "@MARK01i"
ADMIN_ID = 7758666677

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

CONFIG_FILE = "config.json"
USERS_FILE = "users.json"

# تحميل الإعدادات
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"active": True}, f)
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# تسجيل المستخدمين
def add_user(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE) as f:
        users = json.load(f)
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# التحقق من الاشتراك
def check_subscription(user_id):
    try:
        res = bot.get_chat_member(CHANNEL_ID, user_id)
        return res.status in ['member', 'creator', 'administrator']
    except:
        return False

# /start
@bot.message_handler(commands=['start'])
def start(message):
    config = load_config()
    if not config.get("active", True) and message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ البوت متوقف حالياً من قبل الإدارة.")
    
    if not check_subscription(message.from_user.id):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        keyboard.add(InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_sub"))
        return bot.send_message(message.chat.id, "🔒 يجب الاشتراك في القناة لاستخدام البوت:", reply_markup=keyboard)

    add_user(message.from_user.id)
    bot.send_message(message.chat.id, "👋 أهلاً بك! أرسل الآن رابط أي فيديو وسأقوم بتحميله لك.")

# زر تحقق الاشتراك
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def verify_sub(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق من الاشتراك!")
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم العثور على اشتراك!")

# استقبال الروابط
@bot.message_handler(func=lambda msg: msg.text.startswith("http"))
def handle_link(message):
    config = load_config()
    if not config.get("active", True) and message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ البوت متوقف حالياً من قبل الإدارة.")
    
    if not check_subscription(message.from_user.id):
        return start(message)

    add_user(message.from_user.id)
    bot.send_chat_action(message.chat.id, "upload_video")
    
    url = message.text
    try:
        bot.send_message(message.chat.id, f"📥 جاري تحميل الفيديو...\n{url}")
        # مثال API (استخدم API حقيقي للمنصات المتعددة)
        res = requests.get(f"https://api.tikmate.cc/api/download?url={url}")
        file_url = res.json().get("video")
        if file_url:
            bot.send_video(message.chat.id, file_url, caption="✅ تم تحميل الفيديو بنجاح!")
        else:
            bot.send_message(message.chat.id, "❌ لم أتمكن من تحميل الفيديو. تحقق من الرابط.")
    except:
        bot.send_message(message.chat.id, "⚠️ حدث خطأ أثناء التحميل.")

# /admin لوحة تحكم الأدمن
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    config = load_config()
    status = "🟢 يعمل" if config.get("active", True) else "🔴 متوقف"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("📢 إرسال رسالة جماعية", callback_data="broadcast"),
        InlineKeyboardButton("👥 عدد المستخدمين", callback_data="count"),
    )
    keyboard.add(
        InlineKeyboardButton("🛑 إيقاف البوت" if config.get("active", True) else "✅ تشغيل البوت", callback_data="toggle")
    )
    bot.send_message(message.chat.id, f"🎛 لوحة تحكم الأدمن:\n\nالحالة الحالية: {status}", reply_markup=keyboard)

# رد على أزرار لوحة التحكم
@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    if call.data == "count":
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE) as f:
                users = json.load(f)
            bot.answer_callback_query(call.id, f"👥 عدد المستخدمين: {len(users)}")
        else:
            bot.answer_callback_query(call.id, "لا يوجد مستخدمون بعد.")

    elif call.data == "broadcast":
        bot.send_message(call.message.chat.id, "📝 أرسل الآن الرسالة التي تريد إرسالها للجميع.")
        bot.register_next_step_handler(call.message, send_broadcast)

    elif call.data == "toggle":
        config = load_config()
        config["active"] = not config.get("active", True)
        save_config(config)
        new_status = "✅ تم تشغيل البوت." if config["active"] else "🛑 تم إيقاف البوت."
        bot.send_message(call.message.chat.id, new_status)

# إرسال رسالة جماعية
def send_broadcast(message):
    if not os.path.exists(USERS_FILE):
        return bot.send_message(message.chat.id, "⚠️ لا يوجد مستخدمون.")
    with open(USERS_FILE) as f:
        users = json.load(f)
    count = 0
    for user_id in users:
        try:
            bot.copy_message(user_id, message.chat.id, message.message_id)
            count += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم إرسال الرسالة إلى {count} مستخدم.")

# غير ذلك
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "📎 أرسل رابط فيديو لتحميله من TikTok أو إنستقرام أو تويتر...")

# Webhook
@app.route('/', methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

@app.route('/', methods=["GET"])
def index():
    return "بوت تحميل الفيديوهات يعمل ✅", 200

if __name__ == '__main__':
    app.run()
