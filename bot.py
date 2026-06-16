import os
from flask import Flask
from threading import Thread

# Render uchun kichik veb-server
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
import telebot
from telebot import types

bot = telebot.TeleBot('8668561818:AAFRVEpnNhGOMZqO8CQt0TUQz-s102xW0oA')

# Juftliklar ro'yxati
pairs = ["XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "NAS100", "SPX500"]

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(pair, callback_data=pair) for pair in pairs]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Analiz qilmoqchi bo'lgan instrumentni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.send_message(call.message.chat.id, f"✅ {call.data} tanlandi.\n\nEndi *Balans, Risk%, Entry, SL* qiymatlarini probel bilan yozing:", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def calculate(message):
    try:
        b, r, e, sl = map(float, message.text.split())
        lot = (b * (r / 100)) / abs(e - sl)
        bot.reply_to(message, f"📊 *Hisob-kitob natijasi*\n\n💎 Kerakli Lot: `{lot:.4f}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Xatolik! 4 ta raqamni probel bilan kiriting.")
if __name__ == "__main__":
    keep_alive()  # Serverni ishga tushirish
    # Bu yerda pastda botingizni ishga tushirish kodi (polling) tursin
bot.polling()
