import telebot
from flask import Flask, request
import threading
import time
import os
import yt_dlp
from telebot import types

TOKEN = "8116602303:AAHuS7IZt5jivjG68XL3AIVAasCpUcZRLic"
bot = telebot.TeleBot(TOKEN)
WEBHOOK_URL = "https://webhokbot-production.up.railway.app/"

app = Flask(__name__)

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

# إعدادات الملفات والصلاحيات
USERS_FILE = "users.txt"
BANNED_FILE = "banned.txt"
ADMINS = [7758666677]
FORCE_CHANNEL = "MARK01i"

# وظائف مساعدة
def save_user(user_id):
    try:
        with open(USERS_FILE, "a+") as f:
            f.seek(0)
            users = f.read().splitlines()
            if str(user_id) not in users:
                f.write(str(user_id) + "\n")
    except: pass

def is_banned(user_id):
    try:
        with open(BANNED_FILE, "r") as f:
            return str(user_id) in f.read().splitlines()
    except: return False

def check_subscription(user_id):
    try:
        chat_member = bot.get_chat_member(f"@{FORCE_CHANNEL}", user_id)
        return chat_member.status in ['member', 'creator', 'administrator']
    except: return False

# الأزرار
def main_buttons(user_id):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons.row("📤 أرسل رابط فيديو", "ℹ️ تعليمات")
    buttons.row("💬 الدعم الفني")
    if user_id in ADMINS:
        buttons.row("⚙️ إدارة البوت")
    return buttons

def admin_buttons():
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons.row("👥 عدد المستخدمين", "📢 إرسال إعلان")
    buttons.row("🚫 حظر مستخدم", "✅ فك الحظر")
    buttons.row("📨 رسالة خاصة", "🔙 رجوع")
    return buttons

# واجهة البداية
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return bot.send_message(user_id, "❌ أنت محظور من استخدام البوت.")
    if not check_subscription(user_id):
        join_btn = types.InlineKeyboardMarkup()
        join_btn.add(types.InlineKeyboardButton("📢 اشترك الآن", url=f"https://t.me/{FORCE_CHANNEL}"))
        return bot.send_message(user_id, "🚫 يجب الاشتراك في القناة لاستخدام البوت:", reply_markup=join_btn)
    save_user(user_id)
    bot.send_message(user_id,
        "👋 *مرحباً بك في بوت تحميل الفيديوهات!*

"
        "🎥 *يدعم التحميل من TikTok، YouTube، Instagram، Pinterest، وغيرها!*

"
        "📥 *أرسل رابط الفيديو لتحميله فوراً.*",
        parse_mode="Markdown",
        reply_markup=main_buttons(user_id))
    bot.send_message(user_id, "✅ أرسل الآن رابط الفيديو الذي تريد تحميله:", reply_markup=main_buttons(user_id))

# تعليمات
@bot.message_handler(func=lambda m: m.text == "ℹ️ تعليمات")
def show_help(message):
    bot.send_message(message.chat.id,
    "📌 *تعليمات الاستخدام:*
"
    "1. أرسل رابط فيديو من TikTok أو YouTube...
"
    "2. انتظر التحميل.
"
    "3. استلم الفيديو مباشرة ✅", parse_mode="Markdown")

# دعم فني
@bot.message_handler(func=lambda m: m.text == "💬 الدعم الفني")
def support_info(message):
    bot.send_message(message.chat.id, "📨 تواصل مع الدعم: @M_A_R_K75")

# طلب رابط
@bot.message_handler(func=lambda m: m.text == "📤 أرسل رابط فيديو")
def ask_for_link(message):
    bot.send_message(message.chat.id, "✅ *أرسل الآن رابط الفيديو:*", parse_mode="Markdown")

# تحميل فيديو
def download_video(url, chat_id):
    os.makedirs("temp", exist_ok=True)
    output = f"temp/{chat_id}.mp4"
    opts = {'format': 'mp4', 'outtmpl': output, 'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
        return output
    except Exception as e:
        print("Download error:", e)
        return None

@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_link(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return bot.send_message(user_id, "❌ أنت محظور من استخدام البوت.")
    if not check_subscription(user_id):
        join_btn = types.InlineKeyboardMarkup()
        join_btn.add(types.InlineKeyboardButton("📢 اشترك الآن", url=f"https://t.me/{FORCE_CHANNEL}"))
        return bot.send_message(user_id, "🚫 يجب الاشتراك في القناة لاستخدام البوت:", reply_markup=join_btn)
    save_user(user_id)
    msg = bot.send_message(user_id, "⏳ جاري تحميل الفيديو...")
    path = download_video(message.text, user_id)
    if path and os.path.exists(path):
        with open(path, "rb") as vid: bot.send_video(user_id, vid)
        os.remove(path)
        bot.delete_message(user_id, msg.message_id)
    else:
        bot.send_message(user_id, "⚠️ لم أتمكن من تحميل الفيديو.")

# لوحة الإدارة
@bot.message_handler(func=lambda m: m.text == "⚙️ إدارة البوت" and m.from_user.id in ADMINS)
def show_admin_panel(message):
    bot.send_message(message.chat.id, "🛠 مرحباً بك في لوحة الإدارة:", reply_markup=admin_buttons())

@bot.message_handler(func=lambda m: m.text == "🔙 رجوع")
def back_to_main(message):
    bot.send_message(message.chat.id, "⬅️ عدنا للواجهة الرئيسية", reply_markup=main_buttons(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "👥 عدد المستخدمين" and m.from_user.id in ADMINS)
def user_count(message):
    try:
        with open(USERS_FILE, "r") as f:
            count = len(f.read().splitlines())
        bot.send_message(message.chat.id, f"👥 عدد المستخدمين: {count}")
    except:
        bot.send_message(message.chat.id, "❌ لا يوجد بيانات.")

@bot.message_handler(func=lambda m: m.text == "📢 إرسال إعلان" and m.from_user.id in ADMINS)
def ask_broadcast(message):
    sent_msg = bot.send_message(message.chat.id, "📝 أرسل الآن نص الإعلان:")
    bot.register_next_step_handler(sent_msg, broadcast_message)

def broadcast_message(message):
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
        for uid in users:
            try:
                bot.send_message(uid, f"📢 إعلان من الإدارة:

{message.text}")
                time.sleep(0.1)
            except: continue
        bot.send_message(message.chat.id, "✅ تم إرسال الإعلان.")
    except:
        bot.send_message(message.chat.id, "❌ حدث خطأ أثناء الإرسال.")

@bot.message_handler(func=lambda m: m.text == "🚫 حظر مستخدم" and m.from_user.id in ADMINS)
def ask_ban(message):
    msg = bot.send_message(message.chat.id, "✏️ أرسل آيدي المستخدم لحظره:")
    bot.register_next_step_handler(msg, ban_user)

def ban_user(message):
    with open(BANNED_FILE, "a") as f:
        f.write(str(message.text.strip()) + "\n")
    bot.send_message(message.chat.id, f"🚫 تم حظر المستخدم {message.text}")

@bot.message_handler(func=lambda m: m.text == "✅ فك الحظر" and m.from_user.id in ADMINS)
def ask_unban(message):
    msg = bot.send_message(message.chat.id, "✏️ أرسل آيدي المستخدم لفك الحظر:")
    bot.register_next_step_handler(msg, unban_user)

def unban_user(message):
    try:
        with open(BANNED_FILE, "r") as f:
            lines = f.readlines()
        with open(BANNED_FILE, "w") as f:
            for line in lines:
                if line.strip() != message.text.strip():
                    f.write(line)
        bot.send_message(message.chat.id, f"✅ تم فك الحظر عن {message.text}")
    except:
        bot.send_message(message.chat.id, "❌ فشل في فك الحظر.")

@bot.message_handler(func=lambda m: m.text == "📨 رسالة خاصة" and m.from_user.id in ADMINS)
def ask_pm(message):
    msg = bot.send_message(message.chat.id, "✉️ أرسل الآيدي ثم الرسالة بالشكل:\n\n123456 رسالة")
    bot.register_next_step_handler(msg, pm_send)

def pm_send(message):
    try:
        uid, txt = message.text.strip().split(" ", 1)
        bot.send_message(int(uid), f"📩 رسالة من الأدمن:\n\n{txt}")
        bot.send_message(message.chat.id, "✅ تم الإرسال.")
    except:
        bot.send_message(message.chat.id, "❌ صيغة خاطئة. استخدم:\n123456 رسالة")

def run_app():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_app).start()
bot.infinity_polling()
