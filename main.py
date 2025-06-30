import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
from flask import Flask, request

# ✅ بيانات البوت
TOKEN = '7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw'
CHANNEL_USERNAME = '@MARK01i'
FILE_PATH = 'base (5).apk'
TON_WALLET = 'UQBlb6VcwNhEAd9i_6MgTKlGgvGeUAIfL4Q9B7zTOeHwP37r'
PRICE_IN_STARS = 1500

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ التحقق من الاشتراك في القناة
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# ✅ زر الدفع بالنجوم
def payment_button():
    markup = InlineKeyboardMarkup()
    buy_btn = InlineKeyboardButton(
        text=f'💫 شراء تطبيق الاختراق - {PRICE_IN_STARS} نجمة',
        pay=True
    )
    markup.add(buy_btn)
    return markup

# ✅ زر الاشتراك الإجباري
def join_channel_button():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📢 اشترك في القناة", url=f'https://t.me/{CHANNEL_USERNAME.strip("@")}'),
        InlineKeyboardButton("✅ تحقّق من الاشتراك", callback_data='check_sub')
    )
    return markup

# ✅ أمر /start
@bot.message_handler(commands=['start'])
def start(message: Message):
    if not is_user_subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🚫 لا يمكنك استخدام البوت قبل الاشتراك في القناة.\n\n📢 يرجى الاشتراك في القناة ثم الضغط على زر التحقق.",
            reply_markup=join_channel_button()
        )
        return

    bot.send_invoice(
        message.chat.id,
        title='تطبيق الاختراق',
        description='احصل على تطبيق الاختراق الكامل بعد الدفع.',
        provider_token='STARS',
        currency='usd',
        prices=[{'label': 'سعر التطبيق', 'amount': PRICE_IN_STARS * 100}],  # يتم الضرب في 100 لأن Telegram يعمل بالسنت
        start_parameter='buy_file',
        invoice_payload='purchase_app'
    )

# ✅ معالجة الدفع
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

# ✅ عند نجاح الدفع
@bot.message_handler(content_types=['successful_payment'])
def send_file(message: Message):
    bot.send_message(message.chat.id, "✅ تم الدفع بنجاح! جاري إرسال تطبيق الاختراق...")
    with open(FILE_PATH, 'rb') as f:
        bot.send_document(message.chat.id, f)

# ✅ زر تحقق الاشتراك
@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_subscription(call):
    if is_user_subscribed(call.from_user.id):
        bot.send_message(call.message.chat.id, "✅ تم التحقق من الاشتراك! يمكنك الآن شراء التطبيق.")
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ أنت لم تشترك بعد!", show_alert=True)

# ✅ Webhook
@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200

# ✅ بدء التشغيل
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://رابط-مشروعك.railway.app/')
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
