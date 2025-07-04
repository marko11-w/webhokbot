import json
from datetime import datetime
from flask import Flask, request
import telebot
import threading
import time
import os
from telebot import types
import yt_dlp
import requests
from bs4 import BeautifulSoup

# --- إعدادات البوت ---
TOKEN = "8116602303:AAHuS7IZt5jivjG68XL3AIVAasCpUcZRLic"
WEBHOOK_URL = "https://webhokbot-production-421f.up.railway.app/"
ADMINS = [7758666677]
FORCE_CHANNEL = "MARK01i"
DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- حفظ المستخدمين ---
def save_user(user_id):
    user_id = str(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({}, f)
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        if user_id not in data:
            data[user_id] = now
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving user:", e)

# --- التحقق من الاشتراك ---
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(f"@{FORCE_CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# --- أزرار ---
def main_buttons(user_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📤 أرسل رابط فيديو", "ℹ️ تعليمات")
    kb.row("💬 الدعم")
    if user_id in ADMINS:
        kb.row("👥 عدد المستخدمين", "📢 إرسال إعلان")
    return kb

# --- Flask webhook routes ---
@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)

# --- تحميل فيديوهات Instagram بدون كوكيز ---
def download_instagram_video(url):
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        resp = session.post(
            "https://snapinsta.app/action.php",
            data={"url": url, "action": "post"},
            headers=headers
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        video_url = soup.find("a", {"target": "_blank"})
        if video_url:
            return video_url["href"]
        else:
            return None
    except Exception as e:
        print("Instagram download error:", e)
        return None

# --- تحميل باقي الفيديوهات ---
def download_video(url, chat_id):
    os.makedirs("temp", exist_ok=True)
    output = f"temp/{chat_id}.mp4"
    opts = {
        'format': 'mp4',
        'outtmpl': output,
        'quiet': True,
        'no_warnings': True
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return output
    except Exception as e:
        print("Download error:", e)
        return None

# --- أوامر البوت ---
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        btn = types.InlineKeyboardMarkup()
        btn.add(types.InlineKeyboardButton("📢 اشترك الآن", url=f"https://t.me/{FORCE_CHANNEL}"))
        return bot.send_message(user_id, "🚫 يجب الاشتراك في القناة لاستخدام البوت:", reply_markup=btn)
    save_user(user_id)
    bot.send_message(user_id, "👋 مرحباً بك في بوت تحميل الفيديوهات!", reply_markup=main_buttons(user_id))
    bot.send_message(user_id, "✅ أرسل رابط الفيديو الآن ليتم تحميله لك:")

@bot.message_handler(func=lambda m: m.text == "ℹ️ تعليمات")
def help_msg(message):
    bot.send_message(message.chat.id, "📌 أرسل رابط أي فيديو من TikTok أو YouTube أو Instagram لتحميله فوراً.")

@bot.message_handler(func=lambda m: m.text == "💬 الدعم")
def support_msg(message):
    bot.send_message(message.chat.id, "📨 تواصل مع الدعم: @M_A_R_K75")

@bot.message_handler(func=lambda m: m.text == "📤 أرسل رابط فيديو")
def ask_link(message):
    bot.send_message(message.chat.id, "📥 أرسل الآن رابط الفيديو:")

# --- التعامل مع جميع الروابط ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_link(message):
    user_id = message.from_user.id
    url = message.text.strip()

    if not check_subscription(user_id):
        btn = types.InlineKeyboardMarkup()
        btn.add(types.InlineKeyboardButton("📢 اشترك الآن", url=f"https://t.me/{FORCE_CHANNEL}"))
        return bot.send_message(user_id, "🚫 يجب الاشتراك في القناة لاستخدام البوت:", reply_markup=btn)

    save_user(user_id)
    msg = bot.send_message(user_id, "⏳ جاري التحميل...")

    if "instagram.com" in url:
        insta_video = download_instagram_video(url)
        if insta_video:
            bot.send_video(user_id, insta_video)
        else:
            bot.send_message(user_id, "⚠️ لم أتمكن من تحميل فيديو إنستغرام.")
        bot.delete_message(user_id, msg.message_id)
        return

    path = download_video(url, user_id)
    if path and os.path.exists(path):
        with open(path, "rb") as vid:
            bot.send_video(user_id, vid)
        os.remove(path)
    else:
        bot.send_message(user_id, "⚠️ لم أتمكن من تحميل الفيديو.")
    bot.delete_message(user_id, msg.message_id)

# --- عدد المستخدمين ---
@bot.message_handler(func=lambda m: m.text == "👥 عدد المستخدمين" and m.from_user.id in ADMINS)
def show_user_count(message):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        bot.send_message(message.chat.id, f"👥 عدد المستخدمين: {len(data)}")
    except:
        bot.send_message(message.chat.id, "❌ لا يمكن قراءة البيانات.")

# --- إرسال إعلان ---
@bot.message_handler(func=lambda m: m.text == "📢 إرسال إعلان" and m.from_user.id in ADMINS)
def ask_broadcast(message):
    msg = bot.send_message(message.chat.id, "📝 أرسل نص الإعلان:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        success = 0
        fail = 0
        for uid in data:
            try:
                bot.send_message(uid, f"📢 إعلان:\n\n{message.text}")
                success += 1
                time.sleep(0.1)
            except:
                fail += 1
        bot.send_message(message.chat.id, f"✅ تم الإرسال لـ {success} مستخدم.\n❌ فشل: {fail}")
    except:
        bot.send_message(message.chat.id, "❌ حدث خطأ أثناء الإرسال.")

# --- تشغيل السيرفر ---
def run():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run).start()
bot.infinity_polling()
