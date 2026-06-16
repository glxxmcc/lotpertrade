import telebot
from telebot import types

# 1. Tokeningni shu yerga qo'y
TOKEN = '8668561818:AAFRVEpnNhGOMZqO8CQt0TUQz-s102xW0oA'
bot = telebot.TeleBot(TOKEN)

# 2. Instrumentlar uchun punkt qiymatlari (Brokerga qarab o'zgartirishing mumkin)
INSTRUMENT_PIPS = {
    "XAUUSD": 10.0, "XAGUSD": 50.0,
    "BTCUSD": 1.0,   "ETHUSD": 1.0,
    "EURUSD": 10.0,  "GBPUSD": 10.0,
    "NAS100": 1.0,   "SPX500": 1.0
}

user_data = {}

@bot.message_handler(commands=['start', 'calc'])
def start_calc(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    buttons = [types.KeyboardButton(inst) for inst in INSTRUMENT_PIPS.keys()]
    markup.add(*buttons)
    msg = bot.reply_to(message, "Salom! Instrumentni tanla:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_instrument)

def process_instrument(message):
    if message.text not in INSTRUMENT_PIPS:
        bot.reply_to(message, "Iltimos, tugmalardan birini tanlang.")
        return start_calc(message)
    
    user_data[message.chat.id] = {'instrument': message.text}
    msg = bot.reply_to(message, "Balansni kiriting (raqamda):")
    bot.register_next_step_handler(msg, process_balance)

def process_balance(message):
    try:
        user_data[message.chat.id]['balance'] = float(message.text)
        msg = bot.reply_to(message, "Risk foizini kiriting (masalan: 1):")
        bot.register_next_step_handler(msg, process_risk)
    except:
        msg = bot.reply_to(message, "Xato! Faqat raqam kiriting (masalan: 5000):")
        bot.register_next_step_handler(msg, process_balance)

def process_risk(message):
    try:
        user_data[message.chat.id]['risk'] = float(message.text)
        msg = bot.reply_to(message, "Kirish narxini (Entry) kiriting:")
        bot.register_next_step_handler(msg, process_entry)
    except:
        msg = bot.reply_to(message, "Xato! Raqam kiriting (masalan: 1):")
        bot.register_next_step_handler(msg, process_risk)

def process_entry(message):
    try:
        user_data[message.chat.id]['entry'] = float(message.text)
        msg = bot.reply_to(message, "Stop Loss narxini kiriting:")
        bot.register_next_step_handler(msg, process_sl)
    except:
        msg = bot.reply_to(message, "Xato! Narxni raqam bilan kiriting:")
        bot.register_next_step_handler(msg, process_entry)

def process_sl(message):
    try:
        data = user_data[message.chat.id]
        sl = float(message.text)
        inst = data['instrument']
        
        # Hisoblash formulasi
        risk_money = data['balance'] * (data['risk'] / 100)
        sl_dist = abs(data['entry'] - sl)
        pip_val = INSTRUMENT_PIPS[inst]
        
        lot = risk_money / (sl_dist * pip_val)
        
        result = (f"📊 **Natija** ({inst}):\n"
                  f"💰 Balans: {data['balance']}$\n"
                  f"📉 Risk: {data['risk']}% ({risk_money}$)\n"
                  f"📏 SL masofasi: {sl_dist}\n"
                  f"✅ **Tavsiya etilgan lot: {round(lot, 2)}**")
        
        bot.reply_to(message, result, parse_mode="Markdown")
    except:
        bot.reply_to(message, "Xatolik yuz berdi. Iltimos, /calc buyrug'ini boshidan boshlang.")

# Flask qismi (Render uchun)
from flask import Flask
from threading import Thread
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()

bot.polling()
