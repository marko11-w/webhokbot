import telebot
from flask import Flask, request
import threading
import time
import os
import yt_dlp

TOKEN = "8116602303:AAHuS7IZt5jivjG68XL3AIVAasCpUcZRLic"
WEBHOOK_URL = "https://23webhook-production.up.railway.app/"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

# ضبط الويب هوك
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)

# تحميل الفيديو باستخدام yt-dlp
def download_video(url, chat_id):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': f'temp/{chat_id}.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    os.makedirs("temp", exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f'temp/{chat_id}.mp4'
    except Exception as e:
        print("Error downloading:", e)
        return None

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    url = message.text
    if not url.startswith("http"):
        bot.reply_to(message, "❌ الرجاء إرسال رابط صحيح للفيديو.")
        return
    
    msg = bot.send_message(message.chat.id, "⏳ جاري تحميل الفيديو، يرجى الانتظار...")
    video_path = download_video(url, message.chat.id)
    
    if video_path and os.path.exists(video_path):
        try:
            with open(video_path, "rb") as video:
                bot.send_video(message.chat.id, video)
            os.remove(video_path)
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"❌ حدث خطأ أثناء إرسال الفيديو: {e}")
    else:
        bot.edit_message_text("❌ لم أتمكن من تحميل الفيديو. تأكد من صحة الرابط والمنصة المدعومة.", message.chat.id, msg.message_id)

def run_app():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_app).start()
bot.infinity_polling()
