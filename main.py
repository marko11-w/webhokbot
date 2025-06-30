import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import os

# 🔐 بيانات البوت
TOKEN = '7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw'
CHANNEL_USERNAME = '@MARK01i'
FILE_PATH = 'hack_app.apk'
PRICE_IN_STARS = 1500  # بالسنت، لأن تيليجرام يتعامل بـ 100 = 1$

# 🧠 تهيئة البوت و Flask
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ التحقق من الاشتراك الإجباري
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# ✅ أزرار الاشتراك
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
            "🚫 لا يمكنك استخدام البوت قبل الاشتراك في القناة.\n\n📢 اشترك ثم اضغط (تحقق).",
            reply_markup=join_channel_button()
        )
        return

    # ✅ إرسال الفاتورة للشراء
    bot.send_invoice(
        message.chat.id,
        title='تطبيق الاختراق',
        description='احصل على تطبيق الاختراق الكامل بعد الدفع.',
        provider_token='STARS',  # هذا هو مزود Telegram Stars
        currency='usd',
        prices=[{'label': 'سعر التطبيق', 'amount': PRICE_IN_STARS * 100}],  # Telegram uses "cents"
        start_parameter='buy_app',
        invoice_payload='purchase_app'
    )

# ✅ تأكيد الدفع قبل التحصيل
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

# ✅ بعد الدفع، إرسال الملف
@bot.message_handler(content_types=['successful_payment'])
def send_file(message: Message):
    bot.send_message(message.chat.id, "✅ تم الدفع بنجاح! جاري إرسال تطبيق الاختراق...")
    try:
        with open(FILE_PATH, 'rb') as file:
            bot.send_document(message.chat.id, file)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ أثناء إرسال الملف:\n{e}")

# ✅ تحقق من الاشتراك عند الضغط على "تحقق"
@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_subscription(call):
    if is_user_subscribed(call.from_user.id):
        bot.send_message(call.message.chat.id, "✅ تم التحقق من اشتراكك بنجاح! أرسل /start للمتابعة.")
    else:
        bot.answer_callback_query(call.id, "❌ ما زلت غير مشترك في القناة.", show_alert=True)

# ✅ Webhook endpoint
@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

# ✅ تشغيل التطبيق على Railway
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://webhokbot-production-421f.up.railway.app/')  # رابط مشروعك الصحيح
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
