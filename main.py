import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import os

# ✅ بيانات البوت
TOKEN = '7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw'
CHANNEL_USERNAME = '@MARK01i'
FILE_PATH = 'hack_app.apk'
PRICE_IN_STARS = 1500

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ التحقق من الاشتراك
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# ✅ زر الاشتراك الإجباري
def join_channel_button():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📢 اشترك في القناة", url=f'https://t.me/{CHANNEL_USERNAME.strip("@")}'),
        InlineKeyboardButton("✅ تحقّق من الاشتراك", callback_data='check_sub')
    )
    return markup

# ✅ رسالة الترحيب
@bot.message_handler(commands=['start'])
def start(message: Message):
    if not is_user_subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🚫 لا يمكنك استخدام البوت قبل الاشتراك في القناة.\n\n📢 اشترك ثم اضغط تحقق.",
            reply_markup=join_channel_button()
        )
        return

    bot.send_invoice(
        message.chat.id,
        title='تطبيق الاختراق',
        description='احصل على تطبيق الاختراق الكامل بعد الدفع.',
        provider_token='STARS',
        currency='usd',
        prices=[{'label': 'سعر التطبيق', 'amount': PRICE_IN_STARS * 100}],  # ×100 لأن Telegram يستخدم السنت
        start_parameter='buy_file',
        invoice_payload='purchase_app'
    )

# ✅ التحقق من الدفع
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

# ✅ بعد الدفع الكامل
@bot.message_handler(content_types=['successful_payment'])
def send_file(message: Message):
    bot.send_message(message.chat.id, "✅ تم الدفع بنجاح! جاري إرسال تطبيق الاختراق...")
    with open(FILE_PATH, 'rb') as f:
        bot.send_document(message.chat.id, f)

# ✅ زر التحقق من الاشتراك
@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_subscription(call):
    if is_user_subscribed(call.from_user.id):
        bot.send_message(call.message.chat.id, "✅ تم التحقق! اضغط /start للمتابعة.")
    else:
        bot.answer_callback_query(call.id, "❌ أنت لم تشترك بعد.", show_alert=True)

# ✅ استقبال Webhook
@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

# ✅ نقطة التشغيل
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://رابط-مشروعك.railway.app/')
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
