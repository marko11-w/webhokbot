import telebot
from telebot import types
from flask import Flask, request
import json
import os
import logging

# ✅ تفعيل الطباعة للتشخيص على Railway
logging.basicConfig(level=logging.INFO)

API_TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
ADMIN_ID = 7758666677
CHANNEL_USERNAME = "@MARK01i"
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
DATA_FILE = "data.json"

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

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except Exception as e:
        print(f"[Subscription Error]: {e}")
        return True  # مؤقتًا لتجنب التوقف أثناء التجربة

@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    data = load_data()

    if not check_subscription(user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك الآن 📢", url=f"https://t.me/MARK01i"))
        markup.add(types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="check_sub"))
        bot.send_message(user.id, "👋 للمتابعة، اشترك في القناة أولًا:", reply_markup=markup)
        return

    bot.send_message(ADMIN_ID, f"👤 مستخدم جديد\nيوزر: @{user.username or 'غير متوفر'}\nID: {user.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in data["buttons"]:
        markup.add(btn["label"])
    if str(user.id) == str(ADMIN_ID):
        markup.add("⚙️ الأدمن")
    bot.send_message(user.id, "🧠 مرحبًا بك في بوت الاختراق الذكي!\nاختر أحد الأزرار:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if check_subscription(call.from_user.id):
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم الاشتراك بعد.")

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
    msgs = [
        "🔍 جاري تحليل الهدف...",
        "📡 الاتصال بالخوادم...",
        "🧠 تفعيل الذكاء الاصطناعي...",
        "🔓 فك التشفير...",
        "📂 استخراج البيانات...",
        f"✅ كلمة السر المحتملة: pass@{str(message.from_user.id)[-3:]}{label[:3]}",
        "✅ تم الاختراق بنجاح."
    ]
    for msg in msgs:
        bot.send_message(message.chat.id, msg)

# 📡 نقطة الاستقبال من تيليجرام
@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

# 🌐 الصفحة الرئيسية
@app.route("/")
def index():
    return "✅ البوت يعمل!"

# ❗️ إعداد Webhook
bot.remove_webhook()
bot.set_webhook(url="https://webhokbot-bothack.up.railway.app/7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw")

# 🚀 تشغيل الخادم
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
