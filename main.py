import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from flask import Flask, request
import json, os

TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
ADMIN_ID = 7758666677
CHANNEL_USERNAME = "MARK01i"
DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# إنشاء ملف المستخدمين إذا غير موجود
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
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def main_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📘 اختراق فيسبوك", "📷 اختراق انستقرام")
    markup.add("🎥 اختراق تيك توك", "📱 اختراق واتساب")
    markup.add("📶 اختراق واي فاي")
    markup.add("👤 عدد المستخدمين", "📣 رسالة جماعية")
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    data = load_users()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_users(data)
        bot.send_message(ADMIN_ID, f"🆕 مستخدم جديد:\nID: `{user_id}`", parse_mode="Markdown")

    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 اشترك الآن", url=f"https://t.me/{CHANNEL_USERNAME}"))
        return bot.send_message(user_id, "📛 يجب الاشتراك في القناة لاستخدام البوت", reply_markup=markup)

    bot.send_message(user_id, "مرحباً بك في بوت الاختراق الوهمي! اختر نوع الاختراق:", reply_markup=main_buttons())

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    user_id = message.from_user.id
    text = message.text

    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 اشترك الآن", url=f"https://t.me/{CHANNEL_USERNAME}"))
        return bot.send_message(user_id, "📛 يجب الاشتراك في القناة لاستخدام البوت", reply_markup=markup)

    if text in ["📘 اختراق فيسبوك", "📷 اختراق انستقرام", "🎥 اختراق تيك توك", "📱 اختراق واتساب"]:
        msg = bot.send_message(user_id, "📥 أرسل رابط الحساب أو رقم الهاتف:")
        bot.register_next_step_handler(msg, process_fake_hack)
    elif text == "📶 اختراق واي فاي":
        bot.send_message(user_id, "🔍 جاري البحث عن الشبكات القريبة...")
        bot.send_message(user_id, "📡 تم العثور على شبكة محمية... جاري تجربة الاختراق...")
        bot.send_message(user_id, "✅ تم التوصيل بنجاح!\n(وهمي فقط للضحك 😂)")
    elif text == "👤 عدد المستخدمين" and user_id == ADMIN_ID:
        data = load_users()
        bot.send_message(user_id, f"👥 عدد المستخدمين: {len(data['users'])}")
    elif text == "📣 رسالة جماعية" and user_id == ADMIN_ID:
        msg = bot.send_message(user_id, "✉️ أرسل الرسالة الآن:")
        bot.register_next_step_handler(msg, broadcast)

def process_fake_hack(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "🔓 جاري معالجة البيانات...")
    bot.send_message(user_id, "⚙️ تم الوصول إلى الحساب!")
    bot.send_message(user_id, "✅ تمت العملية بنجاح!\n(وهمية فقط للترفيه 🎭)")

def broadcast(message):
    data = load_users()
    for uid in data["users"]:
        try:
            bot.send_message(uid, message.text)
        except:
            pass
    bot.send_message(message.chat.id, "✅ تم إرسال الرسالة إلى الجميع.")

# Webhook endpoints
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "بوت الاختراق يعمل ✅"

bot.remove_webhook()
bot.set_webhook(url=f"https://charhbot-production.up.railway.app/{TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
