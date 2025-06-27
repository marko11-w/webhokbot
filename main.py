import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask, request
import os

# ======= CONFIG =======
API_TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
CHANNEL_USERNAME = "MARK01i"
ADMIN_USERNAME = "@M_A_R_K75"
WEBHOOK_URL = "https://webhokbot-bothack.up.railway.app/" + API_TOKEN
# ======================

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ✅ عرض رسالة الاشتراك فقط
def send_restriction_message(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME}"))
    bot.send_message(
        user_id,
        "🚫 عليك مراسلة الأدمن لتفعيل الاشتراك.\n💸 سعر الاشتراك: 25  دولار \n🧑‍💼 الأدمن: " + ADMIN_USERNAME,
        reply_markup=markup
    )

# ✅ جميع الرسائل والأوامر
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    send_restriction_message(message.chat.id)

# ✅ جميع ضغطات الأزرار (callback buttons)
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    send_restriction_message(call.message.chat.id)

# ✅ Webhook Endpoint
@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "Bot is Running."

# ✅ إعداد Webhook
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# ✅ تشغيل Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
