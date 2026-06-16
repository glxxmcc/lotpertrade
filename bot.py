import telebot
from telebot import types

TOKEN = '8668561818:AAFRVEpnNhGOMZqO8CQt0TUQz-s102xW0oA'
bot = telebot.TeleBot(TOKEN)

INSTRUMENT_PIPS = {
    "XAUUSD": 10.0, "XAGUSD": 50.0,
    "BTCUSD": 1.0,   "ETHUSD": 1.0,
    "EURUSD": 10.0,  "GBPUSD": 10.0,
    "NAS100": 1.0,   "SPX500": 1.0
}

user_state = {}

# Asosiy klaviatura (Murojaat tugmasi bilan)
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 Calc / Start"), types.KeyboardButton("📩 Murojaat"))
    return markup

# Instrument tanlash tugmalari
def get_instruments():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(inst, callback_data=inst) for inst in INSTRUMENT_PIPS.keys()]
    markup.add(*buttons)
    return markup

# Restart tugmasi
def get_restart_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Qaytadan boshlash", callback_data="restart"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Salom! Trading botga xush kelibsiz.", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "🚀 Calc / Start")
def start_calc(message):
    bot.send_message(message.chat.id, "Instrumentni tanlang:", reply_markup=get_instruments())

@bot.message_handler(func=lambda message: message.text == "📩 Murojaat")
def contact_admin(message):
    bot.send_message(message.chat.id, "Taklif va murojaatlar uchun: @Shukurillo_M")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "restart" or call.data in INSTRUMENT_PIPS:
        if call.data != "restart":
            user_state[chat_id] = {'inst': call.data}
        bot.send_message(chat_id, "Balansni kiriting:")
        bot.register_next_step_handler(call.message, get_balance)

def get_balance(message):
    try:
        user_state[message.chat.id]['bal'] = float(message.text)
        bot.send_message(message.chat.id, "Risk % ni kiriting:")
        bot.register_next_step_handler(message, get_risk)
    except:
        bot.send_message(message.chat.id, "Faqat raqam kiriting!")
        bot.register_next_step_handler(message, get_balance)

def get_risk(message):
    try:
        user_state[message.chat.id]['risk'] = float(message.text)
        bot.send_message(message.chat.id, "Entry narxini kiriting:")
        bot.register_next_step_handler(message, get_entry)
    except:
        bot.send_message(message.chat.id, "Faqat raqam kiriting!")
        bot.register_next_step_handler(message, get_risk)

def get_entry(message):
    try:
        user_state[message.chat.id]['entry'] = float(message.text)
        bot.send_message(message.chat.id, "Stop Loss narxini kiriting:")
        bot.register_next_step_handler(message, get_sl)
    except:
        bot.send_message(message.chat.id, "Faqat raqam kiriting!")
        bot.register_next_step_handler(message, get_entry)

def get_sl(message):
    try:
        data = user_state[message.chat.id]
        sl = float(message.text)
        dist = abs(data['entry'] - sl)
        lot = (data['bal'] * (data['risk'] / 100)) / (dist * INSTRUMENT_PIPS[data['inst']])
        
        bot.send_message(message.chat.id, f"✅ **{data['inst']} uchun lot:** {round(lot, 2)}", 
                         reply_markup=get_restart_button(), parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "Xato yuz berdi.", reply_markup=get_restart_button())

# Flask server qismi (render uchun)
from flask import Flask
from threading import Thread
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

bot.polling()
