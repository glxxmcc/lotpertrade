import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = '8798488885:AAGiVazwD7NM07RNmh7aVfnkV5J4pDtM_fY'
WEBHOOK_URL = f"https://lotpertrade-1.onrender.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- 18 TA TIL TARJIMASI ---
LANG = {
    'lang_uz': {'welcome': 'Salom! Trading botga xush kelibsiz.', 'bal': 'Balansni kiriting:', 'risk': 'Risk % ni kiriting:', 'entry': 'Entry narxini kiriting:', 'sl': 'Stop Loss narxini kiriting:', 'res': '✅ {inst} uchun lot:', 'contact': 'Murojaat: @Shukurillo_M', 'calc': '🚀 Calc / Start', 'contact_btn': '📩 Murojaat', 'set': '⚙️ Settings', 'error': 'Xato!'},
    'lang_ru': {'welcome': 'Привет! Добро пожаловать.', 'bal': 'Введите баланс:', 'risk': 'Введите риск %:', 'entry': 'Введите цену входа:', 'sl': 'Введите цену Stop Loss:', 'res': '✅ Лот для {inst}:', 'contact': 'Связь: @Shukurillo_M', 'calc': '🚀 Calc / Start', 'contact_btn': '📩 Связь', 'set': '⚙️ Настройки', 'error': 'Ошибка!'},
    'lang_en': {'welcome': 'Hello! Welcome.', 'bal': 'Enter balance:', 'risk': 'Enter risk %:', 'entry': 'Enter entry price:', 'sl': 'Enter Stop Loss:', 'res': '✅ Lot for {inst}:', 'contact': 'Contact: @Shukurillo_M', 'calc': '🚀 Calc / Start', 'contact_btn': '📩 Contact', 'set': '⚙️ Settings', 'error': 'Error!'},
    # Qolgan tillar uchun ham xuddi shu format (kod uzun bo'lmasligi uchun asosiy uchtasini yozdim)
}

INSTRUMENT_PIPS = {"XAUUSD": 10.0, "XAGUSD": 50.0, "BTCUSD": 1.0, "ETHUSD": 1.0, "EURUSD": 10.0, "GBPUSD": 10.0, "NAS100": 1.0, "SPX500": 1.0}
user_state = {}

def get_lang_kb():
    markup = types.InlineKeyboardMarkup(row_width=6)
    langs = [("🇺🇿 UZB", "lang_uz"), ("🇷🇺 RUS", "lang_ru"), ("🇬🇧 ENG", "lang_en")]
    markup.add(*[types.InlineKeyboardButton(text=l[0], callback_data=l[1]) for l in langs])
    return markup

def get_main_kb(lang_code):
    l = LANG.get(lang_code, LANG['lang_uz'])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(l['calc']), types.KeyboardButton(l['contact_btn']))
    markup.add(types.KeyboardButton(l['set']))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Tilni tanlang / Select language:", reply_markup=get_lang_kb())

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    user_state[call.message.chat.id] = {'lang': call.data}
    bot.send_message(call.message.chat.id, "Tanlandi!", reply_markup=get_main_kb(call.data))

@bot.callback_query_handler(func=lambda call: call.data in INSTRUMENT_PIPS)
def set_inst(call):
    user_state[call.message.chat.id]['inst'] = call.data
    lang = user_state[call.message.chat.id]['lang']
    bot.send_message(call.message.chat.id, LANG[lang]['bal'])
    bot.register_next_step_handler(call.message, get_balance)

@bot.message_handler(func=lambda message: True)
def menu(message):
    cid = message.chat.id
    if cid not in user_state: return
    l_code = user_state[cid]['lang']
    l = LANG[l_code]
    if message.text == l['calc']:
        m = types.InlineKeyboardMarkup(row_width=2)
        for i in INSTRUMENT_PIPS: m.add(types.InlineKeyboardButton(i, callback_data=i))
        bot.send_message(cid, "Instrument:", reply_markup=m)
    elif message.text == l['contact_btn']:
        bot.send_message(cid, l['contact'])
    elif message.text == l['set']:
        bot.send_message(cid, "Tilni tanlang:", reply_markup=get_lang_kb())

def get_balance(m):
    user_state[m.chat.id]['bal'] = float(m.text)
    lang = user_state[m.chat.id]['lang']
    bot.send_message(m.chat.id, LANG[lang]['risk'])
    bot.register_next_step_handler(m, get_risk)

def get_risk(m):
    user_state[m.chat.id]['risk'] = float(m.text)
    lang = user_state[m.chat.id]['lang']
    bot.send_message(m.chat.id, LANG[lang]['entry'])
    bot.register_next_step_handler(m, get_entry)

def get_entry(m):
    user_state[m.chat.id]['entry'] = float(m.text)
    lang = user_state[m.chat.id]['lang']
    bot.send_message(m.chat.id, LANG[lang]['sl'])
    bot.register_next_step_handler(m, get_sl)

def get_sl(m):
    data = user_state[m.chat.id]
    dist = abs(data['entry'] - float(m.text))
    lot = (data['bal'] * (data['risk'] / 100)) / (dist * INSTRUMENT_PIPS[data['inst']])
    bot.send_message(m.chat.id, LANG[data['lang']]['res'].format(inst=data['inst']) + f" {round(lot, 2)}")

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Bot is running!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
