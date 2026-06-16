import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = '8798488885:AAGiVazwD7NM07RNmh7aVfnkV5J4pDtM_fY'
WEBHOOK_URL = f"https://lotpertrade-1.onrender.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

INSTRUMENT_PIPS = {
    "XAUUSD": 10.0, "XAGUSD": 50.0,
    "BTCUSD": 1.0,   "ETHUSD": 1.0,
    "EURUSD": 10.0,  "GBPUSD": 10.0,
    "NAS100": 1.0,   "SPX500": 1.0
}

user_state = {}

# --- TIL VA MENYU FUNKSIYALARI ---

def get_language_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=6)
    languages = [
        ("🇺🇿 UZB", "lang_uz"), ("🇷🇺 RUS", "lang_ru"), ("🇬🇧 ENG", "lang_en"),
        ("🇹🇷 TUR", "lang_tr"), ("🇩🇪 GER", "lang_de"), ("🇫🇷 FRA", "lang_fr"),
        ("🇪🇸 ESP", "lang_es"), ("🇮🇹 ITA", "lang_it"), ("🇵🇹 POR", "lang_pt"),
        ("🇯🇵 JPN", "lang_ja"), ("🇨🇳 CHI", "lang_zh"), ("🇰🇷 KOR", "lang_ko"),
        ("🇸🇦 ARA", "lang_ar"), ("🇮🇳 HIN", "lang_hi"), ("🇳🇱 DUT", "lang_nl"),
        ("🇸🇪 SWE", "lang_sv"), ("🇵🇱 POL", "lang_pl"), ("🇻🇳 VIE", "lang_vi")
    ]
    buttons = [types.InlineKeyboardButton(text=lang[0], callback_data=lang[1]) for lang in languages]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"))
    return markup

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 Calc / Start"), types.KeyboardButton("⚙️ Settings"))
    return markup

def get_instruments():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(inst, callback_data=inst) for inst in INSTRUMENT_PIPS.keys()]
    markup.add(*buttons)
    return markup

def get_restart_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Qaytadan boshlash", callback_data="restart"))
    return markup

# --- HANDLERLAR ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Tilni tanlang / Выберите язык / Select language:", reply_markup=get_language_keyboard())

@bot.message_handler(func=lambda message: message.text == "🚀 Calc / Start")
def start_calc(message):
    bot.send_message(message.chat.id, "Instrumentni tanlang:", reply_markup=get_instruments())

@bot.message_handler(func=lambda message: message.text == "⚙️ Settings")
def settings_menu(message):
    bot.send_message(message.chat.id, "Sozlamalar. Tilni o'zgartirish:", reply_markup=get_language_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data.startswith("lang_"):
        user_state[chat_id] = {'lang': call.data}
        bot.answer_callback_query(call.id, "Til tanlandi!")
        bot.send_message(chat_id, "Endi asosiy menyudan foydalanishingiz mumkin:", reply_markup=get_main_keyboard())
    elif call.data == "settings":
        bot.send_message(chat_id, "Tilni tanlang:", reply_markup=get_language_keyboard())
    elif call.data == "restart" or call.data in INSTRUMENT_PIPS:
        if call.data != "restart":
            user_state[chat_id]['inst'] = call.data
        bot.send_message(chat_id, "Balansni kiriting:")
        bot.register_next_step_handler(call.message, get_balance)

# --- QOLGAN FUNKSIYALAR (get_balance, get_risk, vb.) O'ZGARISHSZ QOLADI ---
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

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Bot is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    server.run(host="0.0.0.0", port=port)

