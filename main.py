import telebot
from flask import Flask, request
import threading
import time
import os
import yt_dlp
from telebot import types

# ✅ توكن البوت
TOKEN = "8116602303:AAHuS7IZt5jivjG68XL3AIVAasCpUcZRLic"
bot = telebot.TeleBot(TOKEN)

# ✅ رابط Webhook الخاص بـ Railway
WEBHOOK_URL = "https://webhokbot-production-421f.up.railway.app/"

# ✅ إعداد Flask لتشغيل Webhook
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

# ✅ إعداد Webhook في Telegram
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)

# ✅ أزرار البوت
def main_buttons():
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons.row("📤 أرسل رابط فيديو", "ℹ️ تعليمات")
    buttons.row("💬 الدعم الفني")
    return buttons

# ✅ رسالة البدء
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "👋 *مرحباً بك في بوت تحميل الفيديوهات!*\n\n"
        "🎥 *يدعم التحميل من TikTok، YouTube، Instagram، Pinterest، وغيرها!*\n\n"
        "📥 *فقط أرسل رابط الفيديو وسأقوم بتحميله لك فوراً.*",
        parse_mode="Markdown",
        reply_markup=main_buttons()
    )

# ✅ تعليمات الاستخدام
@bot.message_handler(func=lambda m: m.text == "ℹ️ تعليمات")
def show_help(message):
    bot.send_message(message.chat.id,
    "📌 *تعليمات الاستخدام:*\n\n"
    "1. أرسل رابط أي فيديو من TikTok، YouTube، Instagram، Pinterest...\n"
    "2. انتظر قليلاً ليتم تحميل الفيديو 🎬\n"
    "3. سيصلك الفيديو أو رابط مباشر له.\n\n"
    "_جميع التحميلات خاصة ومباشرة_ ✅",
    parse_mode="Markdown")

# ✅ الدعم الفني
@bot.message_handler(func=lambda m: m.text == "💬 الدعم الفني")
def support_info(message):
    bot.send_message(message.chat.id, "📨 للدعم الفني: @M_A_R_K75")

# ✅ استقبال زر "أرسل رابط فيديو"
@bot.message_handler(func=lambda m: m.text == "📤 أرسل رابط فيديو")
def ask_for_link(message):
    bot.send_message(message.chat.id, "✅ *أرسل الآن رابط الفيديو الذي تريد تحميله:*", parse_mode="Markdown")

# ✅ تحميل الفيديو
def download_video(url, chat_id):
    os.makedirs("temp", exist_ok=True)
    output_path = f"temp/{chat_id}.mp4"
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path
    except Exception as e:
        print("خطأ:", e)
        return None

# ✅ استقبال روابط الفيديوهات
@bot.message_handler(func=lambda message: message.text and message.text.startswith("http"))
def handle_link(message):
    msg = bot.send_message(message.chat.id, "⏳ جاري تحميل الفيديو، الرجاء الانتظار...")
    path = download_video(message.text, message.chat.id)

    if path and os.path.exists(path):
        try:
            with open(path, "rb") as vid:
                bot.send_video(message.chat.id, vid)
            os.remove(path)
            bot.delete_message(message.chat.id, msg.message_id)
        except:
            bot.send_message(message.chat.id, "❌ حدث خطأ أثناء إرسال الفيديو.")
    else:
        bot.send_message(message.chat.id, "⚠️ لم أتمكن من تحميل الفيديو. تحقق من الرابط.")

# ✅ تشغيل Flask على Railway
def run_app():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_app).start()
bot.infinity_polling()
