import telebot
from flask import Flask, request
import os

TOKEN = '7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    print("✅ استقبل /start")
    bot.send_message(message.chat.id, "✅ البوت يعمل بنجاح!")

@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://webhokbot-production-421f.up.railway.app/')
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
