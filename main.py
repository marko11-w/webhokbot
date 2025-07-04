import json
import time
import os
import threading
from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types
import yt_dlp
import requests

# --- إعدادات البوت ---
TOKEN = "8116602303:AAHuS7IZt5jivjG68XL3AIVAasCpUcZRLic"
WEBHOOK_URL = "https://webhokbot-production-421f.up.railway.app/"
ADMINS = [7758666677]
FORCE_CHANNEL = "MARK01i"
DATA_FILE = "data.json"

APIFY_TOKEN = "YOUR_APIFY_TOKEN"  # ضع توكن Apify هنا

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# —————————————— وظائف مساعدة ——————————————
def check_subscription(user_id):
    try:
        return bot.get_chat_member(f"@{FORCE_CHANNEL}", user_id).status in ["member","creator","administrator"]
    except:
        return False

def save_user(user_id):
    uid = str(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        data = {}
        if os.path.exists(DATA_FILE):
            data = json.load(open(DATA_FILE))
        if uid not in data:
            data[uid] = now
            json.dump(data, open(DATA_FILE, "w"), indent=4)
    except: pass

def main_buttons(user_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📤 أرسل رابط فيديو", "ℹ️ تعليمات")
    kb.row("💬 الدعم")
    if user_id in ADMINS:
        kb.row("👥 عدد المستخدمين", "📢 إرسال إعلان")
    return kb

# —————————————— Flask Webhook ——————————————
@app.route("/", methods=["GET"])
def home(): return "Bot is running."

@app.route("/", methods=["POST"])
def webhook():
    upd = telebot.types.Update.de_json(request.stream.read().decode())
    bot.process_new_updates([upd])
    return "ok",200

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)

# —————————————— ApiLabs Apify Downloader ——————————————
def download_instagram_with_apify(url):
    try:
        resp = requests.post(
            f"https://api.apify.com/v2/acts/apilabs~instagram-downloader/run-sync-get-dataset-items?token={APIFY_TOKEN}",
            json={"urls":[url],"proxy":{"useApifyProxy":True}}
        )
        items = resp.json().get("items", [])
        if items and "download_link" in items[0]:
            return items[0]["download_link"]
    except Exception as e:
        print("Apify error:", e)
    return None

# —————————————— تحميل TikTok/YouTube عبر yt_dlp ——————————————
def download_video(url, uid):
    os.makedirs("temp", exist_ok=True)
    out = f"temp/{uid}.mp4"
    opts = {'format':'mp4','outtmpl':out,'quiet':True,'no_warnings':True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return out
    except Exception as e:
        print("yt_dlp error:",e)
        return None

# —————————————— أوامر البوت ——————————————
@bot.message_handler(commands=["start"])
def cmd_start(m):
    if not check_subscription(m.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك أولاً", url=f"https://t.me/{FORCE_CHANNEL}"))
        return bot.send_message(m.chat.id,"🚫 اشترك أولاً.",reply_markup=kb)
    save_user(m.from_user.id)
    bot.send_message(m.chat.id,"👋 أهلاً! أرسل الرابط لتحميل الفيديو.",reply_markup=main_buttons(m.from_user.id))

@bot.message_handler(lambda m: m.text=="ℹ️ تعليمات")
def cmd_help(m):
    bot.send_message(m.chat.id,"📌 أرسل رابط فيديو من TikTok أو YouTube أو Instagram.")

@bot.message_handler(lambda m: m.text=="💬 الدعم")
def cmd_support(m):
    bot.send_message(m.chat.id,"📨 تواصل: @M_A_R_K75")

@bot.message_handler(lambda m: m.text=="📢 إرسال إعلان" and m.from_user.id in ADMINS)
def cmd_announce(m):
    msg = bot.send_message(m.chat.id,"📝 أرسل نص الإعلان:")
    bot.register_next_step_handler(msg, send_announce)

def send_announce(m):
    try:
        data = json.load(open(DATA_FILE))
    except:
        data = {}
    s,f=0,0
    for uid in data:
        try:
            bot.send_message(int(uid),f"📣 إعلان:\n\n{m.text}")
            s+=1
            time.sleep(0.1)
        except: f+=1
    bot.send_message(m.chat.id,f"✅ تم: {s}, ❌ فشل: {f}")

@bot.message_handler(lambda m: m.text=="👥 عدد المستخدمين" and m.from_user.id in ADMINS)
def cmd_users(m):
    try:
        data = json.load(open(DATA_FILE))
        bot.send_message(m.chat.id,f"👥 مستخدمين: {len(data)}")
    except:
        bot.send_message(m.chat.id,"❌ خطأ في البيانات")

@bot.message_handler(lambda m: m.text and m.text.startswith("http"))
def cmd_download(m):
    uid = m.from_user.id
    if not check_subscription(uid):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك أولاً", url=f"https://t.me/{FORCE_CHANNEL}"))
        return bot.send_message(uid,"🚫 اشترك أولاً.",reply_markup=kb)

    save_user(uid)
    msg = bot.send_message(uid,"⏳ جاري التحميل...")

    txt = m.text.strip()
    if "instagram.com" in txt:
        video_url = download_instagram_with_apify(txt)
        if video_url:
            bot.send_video(uid, video_url)
        else:
            bot.send_message(uid,"⚠️ فشل تحميل إنستغرام.")
        bot.delete_message(uid,msg.message_id)
        return

    path = download_video(txt, uid)
    if path and os.path.exists(path):
        bot.send_video(uid, open(path, "rb"))
        os.remove(path)
    else:
        bot.send_message(uid,"⚠️ فشل تحميل الفيديو.")
    bot.delete_message(uid,msg.message_id)

# —————————————— تشغيل السيرفر ——————————————
def run_app():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_app).start()
bot.infinity_polling()
