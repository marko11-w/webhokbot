import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask, request
import json
import os

TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
ADMIN_ID = 7758666677
CHANNEL_USERNAME = "MARK01i"
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

def get_main_keyboard(user_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📘 اختراق فيسبوك", callback_data="hack_facebook"))
    kb.add(InlineKeyboardButton("📸 اختراق انستجرام", callback_data="hack_instagram"))
    kb.add(InlineKeyboardButton("🎵 اختراق تيك توك", callback_data="hack_tiktok"))
    kb.add(InlineKeyboardButton("📶 اختراق واي فاي", callback_data="hack_wifi"))
    return kb

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "أهلاً بك في بوت الاختراق المزيف 🎯\nيرجى الضغط على أحد الأزرار لاختيار نوع الاختراق.", reply_markup=get_main_keyboard(user_id))
    # تسجيل المستخدم مع تفعيل الاشتراك تلقائيًا False
    data = load_data()
    user_str = str(user_id)
    if user_str not in data["users"]:
        data["users"][user_str] = {"active": False}
        save_data(data)

@bot.callback_query_handler(func=lambda call: call.data.startswith("hack_"))
def callback_hack(call):
    user_id = call.from_user.id
    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "عليك مراسلة الأدمن لتفعيل الاشتراك.", show_alert=True)
        return
    # بعد التحقق، نطلب من المستخدم إرسال معرف أو رابط الحساب
    bot.answer_callback_query(call.id)
    msg = bot.send_message(user_id, f"📤 أرسل معرف الحساب أو رابط الحساب لـ {call.data[5:].capitalize()}:")
    bot.register_next_step_handler(msg, lambda m: fake_hack_process(m, call.data[5:]))

def fake_hack_process(message, hack_type):
    user_id = message.from_user.id
    target = message.text
    bot.send_message(user_id, "🔍 جاري تحليل الهدف...")
    bot.send_message(user_id, "📡 الاتصال بالخوادم...")
    bot.send_message(user_id, "🧠 تفعيل الذكاء الاصطناعي...")
    # يمكنك إضافة خطوات أخرى وهمية هنا حسب رغبتك
    bot.send_message(user_id, f"✅ تم الحصول على بيانات {hack_type} بنجاح!\n(هذا بوت مزيف للترفيه فقط)")

# --- أوامر الأدمن لتفعيل/تعطيل الاشتراك ---
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text)
def admin_commands(message):
    text = message.text.strip()
    if text.startswith("/activate"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            target_id = parts[1]
            set_subscription(target_id, True)
            bot.send_message(ADMIN_ID, f"تم تفعيل الاشتراك للمستخدم {target_id}")
            bot.send_message(int(target_id), "🎉 تم تفعيل اشتراكك في البوت، يمكنك الآن استخدام الأزرار.")
        else:
            bot.send_message(ADMIN_ID, "استخدام: /activate user_id")
    elif text.startswith("/deactivate"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            target_id = parts[1]
            set_subscription(target_id, False)
            bot.send_message(ADMIN_ID, f"تم تعطيل الاشتراك للمستخدم {target_id}")
            bot.send_message(int(target_id), "⚠️ تم تعطيل اشتراكك في البوت، يرجى مراسلة الأدمن.")
        else:
            bot.send_message(ADMIN_ID, "استخدام: /deactivate user_id")
    elif text == "/list":
        data = load_data()
        users = [f"{uid} - {'مفعل' if info.get('active', False) else 'معطل'}" for uid, info in data["users"].items()]
        msg = "قائمة المستخدمين:\n" + "\n".join(users)
        bot.send_message(ADMIN_ID, msg)

# Flask ويب هوك
from flask import Flask, request
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK"

bot.remove_webhook()
# ضع رابط مشروعك مع التوكن الخاص بك
WEBHOOK_URL = "https://webhokbot-bothack.up.railway.app/" + TOKEN
bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
