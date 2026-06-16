import os
import telebot
from telebot import types
from flask import Flask, request

# --- TOKEN: Environment variable orqali olinadi (xavfsizlik uchun) ---
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable topilmadi! Render Dashboard > Environment bo'limiga qo'shing.")

RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://lotpertrade-1.onrender.com')
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- 12 TA TIL TARJIMASI ---
LANG = {
    'lang_uz': {
        'name': "🇺🇿 O'zbek",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Til tanlandi: O'zbek",
        'bal': "💰 Balansni kiriting (masalan: 1000):",
        'risk': "📊 Risk foizini kiriting (masalan: 2):",
        'entry': "📈 Entry (kirish) narxini kiriting:",
        'sl': "🛑 Stop Loss narxini kiriting:",
        'res': "✅ {inst} uchun lot hajmi:",
        'contact': "📩 Murojaat uchun: @Shukurillo_M",
        'calc': "🚀 Hisoblash",
        'contact_btn': "📩 Murojaat",
        'set': "⚙️ Sozlamalar",
        'instrument': "Instrumentni tanlang:",
        'err_number': "⚠️ Iltimos, faqat raqam kiriting (masalan: 1000 yoki 1850.5)",
        'err_zero_dist': "⚠️ Entry va Stop Loss narxlari bir xil bo'lishi mumkin emas. Qaytadan urinib ko'ring.",
        'err_state': "⚠️ Iltimos, avval /start buyrug'ini bosing.",
        'err_positive': "⚠️ Qiymat noldan katta bo'lishi kerak.",
    },
    'lang_ru': {
        'name': "🇷🇺 Русский",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Язык выбран: Русский",
        'bal': "💰 Введите баланс (например: 1000):",
        'risk': "📊 Введите риск в % (например: 2):",
        'entry': "📈 Введите цену входа (Entry):",
        'sl': "🛑 Введите цену Stop Loss:",
        'res': "✅ Лот для {inst}:",
        'contact': "📩 Связь: @Shukurillo_M",
        'calc': "🚀 Рассчитать",
        'contact_btn': "📩 Связь",
        'set': "⚙️ Настройки",
        'instrument': "Выберите инструмент:",
        'err_number': "⚠️ Пожалуйста, введите только число (например: 1000 или 1850.5)",
        'err_zero_dist': "⚠️ Цены Entry и Stop Loss не могут быть одинаковыми. Попробуйте снова.",
        'err_state': "⚠️ Пожалуйста, сначала нажмите /start.",
        'err_positive': "⚠️ Значение должно быть больше нуля.",
    },
    'lang_en': {
        'name': "🇬🇧 English",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Language selected: English",
        'bal': "💰 Enter your balance (e.g. 1000):",
        'risk': "📊 Enter risk % (e.g. 2):",
        'entry': "📈 Enter Entry price:",
        'sl': "🛑 Enter Stop Loss price:",
        'res': "✅ Lot size for {inst}:",
        'contact': "📩 Contact: @Shukurillo_M",
        'calc': "🚀 Calculate",
        'contact_btn': "📩 Contact",
        'set': "⚙️ Settings",
        'instrument': "Select instrument:",
        'err_number': "⚠️ Please enter a valid number (e.g. 1000 or 1850.5)",
        'err_zero_dist': "⚠️ Entry and Stop Loss prices cannot be the same. Try again.",
        'err_state': "⚠️ Please press /start first.",
        'err_positive': "⚠️ Value must be greater than zero.",
    },
    'lang_tr': {
        'name': "🇹🇷 Türkçe",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Dil seçildi: Türkçe",
        'bal': "💰 Bakiyenizi girin (örnek: 1000):",
        'risk': "📊 Risk yüzdesini girin (örnek: 2):",
        'entry': "📈 Giriş (Entry) fiyatını girin:",
        'sl': "🛑 Stop Loss fiyatını girin:",
        'res': "✅ {inst} için lot büyüklüğü:",
        'contact': "📩 İletişim: @Shukurillo_M",
        'calc': "🚀 Hesapla",
        'contact_btn': "📩 İletişim",
        'set': "⚙️ Ayarlar",
        'instrument': "Enstrüman seçin:",
        'err_number': "⚠️ Lütfen geçerli bir sayı girin (örnek: 1000 veya 1850.5)",
        'err_zero_dist': "⚠️ Entry ve Stop Loss fiyatları aynı olamaz. Tekrar deneyin.",
        'err_state': "⚠️ Lütfen önce /start komutunu çalıştırın.",
        'err_positive': "⚠️ Değer sıfırdan büyük olmalıdır.",
    },
    'lang_ar': {
        'name': "🇸🇦 العربية",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ تم اختيار اللغة: العربية",
        'bal': "💰 أدخل رصيدك (مثال: 1000):",
        'risk': "📊 أدخل نسبة المخاطرة % (مثال: 2):",
        'entry': "📈 أدخل سعر الدخول (Entry):",
        'sl': "🛑 أدخل سعر وقف الخسارة (Stop Loss):",
        'res': "✅ حجم اللوت لـ {inst}:",
        'contact': "📩 للتواصل: @Shukurillo_M",
        'calc': "🚀 احساب",
        'contact_btn': "📩 تواصل",
        'set': "⚙️ الإعدادات",
        'instrument': "اختر الأداة:",
        'err_number': "⚠️ يرجى إدخال رقم صحيح (مثال: 1000 أو 1850.5)",
        'err_zero_dist': "⚠️ لا يمكن أن يكون سعر الدخول وسعر وقف الخسارة متساويين. حاول مرة أخرى.",
        'err_state': "⚠️ يرجى الضغط على /start أولاً.",
        'err_positive': "⚠️ يجب أن تكون القيمة أكبر من الصفر.",
    },
    'lang_zh': {
        'name': "🇨🇳 中文",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ 已选择语言：中文",
        'bal': "💰 请输入余额（例如：1000）：",
        'risk': "📊 请输入风险百分比（例如：2）：",
        'entry': "📈 请输入入场价格（Entry）：",
        'sl': "🛑 请输入止损价格（Stop Loss）：",
        'res': "✅ {inst} 的手数：",
        'contact': "📩 联系方式：@Shukurillo_M",
        'calc': "🚀 计算",
        'contact_btn': "📩 联系",
        'set': "⚙️ 设置",
        'instrument': "选择交易品种：",
        'err_number': "⚠️ 请输入有效数字（例如：1000 或 1850.5）",
        'err_zero_dist': "⚠️ 入场价和止损价不能相同，请重试。",
        'err_state': "⚠️ 请先点击 /start。",
        'err_positive': "⚠️ 数值必须大于零。",
    },
    'lang_es': {
        'name': "🇪🇸 Español",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Idioma seleccionado: Español",
        'bal': "💰 Ingrese su balance (ej: 1000):",
        'risk': "📊 Ingrese el % de riesgo (ej: 2):",
        'entry': "📈 Ingrese el precio de entrada (Entry):",
        'sl': "🛑 Ingrese el precio de Stop Loss:",
        'res': "✅ Tamaño de lote para {inst}:",
        'contact': "📩 Contacto: @Shukurillo_M",
        'calc': "🚀 Calcular",
        'contact_btn': "📩 Contacto",
        'set': "⚙️ Ajustes",
        'instrument': "Seleccione el instrumento:",
        'err_number': "⚠️ Por favor ingrese un número válido (ej: 1000 o 1850.5)",
        'err_zero_dist': "⚠️ Los precios de Entry y Stop Loss no pueden ser iguales. Intente de nuevo.",
        'err_state': "⚠️ Por favor presione /start primero.",
        'err_positive': "⚠️ El valor debe ser mayor que cero.",
    },
    'lang_pt': {
        'name': "🇵🇹 Português",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Idioma selecionado: Português",
        'bal': "💰 Insira seu saldo (ex: 1000):",
        'risk': "📊 Insira o % de risco (ex: 2):",
        'entry': "📈 Insira o preço de entrada (Entry):",
        'sl': "🛑 Insira o preço de Stop Loss:",
        'res': "✅ Tamanho do lote para {inst}:",
        'contact': "📩 Contato: @Shukurillo_M",
        'calc': "🚀 Calcular",
        'contact_btn': "📩 Contato",
        'set': "⚙️ Configurações",
        'instrument': "Selecione o instrumento:",
        'err_number': "⚠️ Por favor insira um número válido (ex: 1000 ou 1850.5)",
        'err_zero_dist': "⚠️ Os preços de Entry e Stop Loss não podem ser iguais. Tente novamente.",
        'err_state': "⚠️ Por favor pressione /start primeiro.",
        'err_positive': "⚠️ O valor deve ser maior que zero.",
    },
    'lang_fr': {
        'name': "🇫🇷 Français",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Langue sélectionnée : Français",
        'bal': "💰 Entrez votre solde (ex: 1000):",
        'risk': "📊 Entrez le % de risque (ex: 2):",
        'entry': "📈 Entrez le prix d'entrée (Entry):",
        'sl': "🛑 Entrez le prix du Stop Loss:",
        'res': "✅ Taille du lot pour {inst}:",
        'contact': "📩 Contact: @Shukurillo_M",
        'calc': "🚀 Calculer",
        'contact_btn': "📩 Contact",
        'set': "⚙️ Paramètres",
        'instrument': "Sélectionnez l'instrument:",
        'err_number': "⚠️ Veuillez entrer un nombre valide (ex: 1000 ou 1850.5)",
        'err_zero_dist': "⚠️ Les prix Entry et Stop Loss ne peuvent pas être identiques. Réessayez.",
        'err_state': "⚠️ Veuillez d'abord appuyer sur /start.",
        'err_positive': "⚠️ La valeur doit être supérieure à zéro.",
    },
    'lang_de': {
        'name': "🇩🇪 Deutsch",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ Sprache ausgewählt: Deutsch",
        'bal': "💰 Geben Sie Ihr Guthaben ein (z.B. 1000):",
        'risk': "📊 Geben Sie das Risiko in % ein (z.B. 2):",
        'entry': "📈 Geben Sie den Einstiegspreis (Entry) ein:",
        'sl': "🛑 Geben Sie den Stop-Loss-Preis ein:",
        'res': "✅ Lotgröße für {inst}:",
        'contact': "📩 Kontakt: @Shukurillo_M",
        'calc': "🚀 Berechnen",
        'contact_btn': "📩 Kontakt",
        'set': "⚙️ Einstellungen",
        'instrument': "Instrument auswählen:",
        'err_number': "⚠️ Bitte geben Sie eine gültige Zahl ein (z.B. 1000 oder 1850.5)",
        'err_zero_dist': "⚠️ Entry- und Stop-Loss-Preise dürfen nicht gleich sein. Versuchen Sie es erneut.",
        'err_state': "⚠️ Bitte drücken Sie zuerst /start.",
        'err_positive': "⚠️ Der Wert muss größer als null sein.",
    },
    'lang_ko': {
        'name': "🇰🇷 한국어",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ 언어가 선택되었습니다: 한국어",
        'bal': "💰 잔액을 입력하세요 (예: 1000):",
        'risk': "📊 리스크 %를 입력하세요 (예: 2):",
        'entry': "📈 진입가(Entry)를 입력하세요:",
        'sl': "🛑 손절가(Stop Loss)를 입력하세요:",
        'res': "✅ {inst}의 로트 크기:",
        'contact': "📩 문의: @Shukurillo_M",
        'calc': "🚀 계산하기",
        'contact_btn': "📩 문의",
        'set': "⚙️ 설정",
        'instrument': "상품 선택:",
        'err_number': "⚠️ 올바른 숫자를 입력해주세요 (예: 1000 또는 1850.5)",
        'err_zero_dist': "⚠️ 진입가와 손절가는 같을 수 없습니다. 다시 시도해주세요.",
        'err_state': "⚠️ 먼저 /start를 눌러주세요.",
        'err_positive': "⚠️ 값은 0보다 커야 합니다.",
    },
    'lang_ja': {
        'name': "🇯🇵 日本語",
        'welcome': "Tilni tanlang / Select language:",
        'chosen': "✅ 言語が選択されました：日本語",
        'bal': "💰 残高を入力してください（例：1000）：",
        'risk': "📊 リスク％を入力してください（例：2）：",
        'entry': "📈 エントリー価格を入力してください：",
        'sl': "🛑 ストップロス価格を入力してください：",
        'res': "✅ {inst} のロットサイズ：",
        'contact': "📩 連絡先：@Shukurillo_M",
        'calc': "🚀 計算する",
        'contact_btn': "📩 連絡先",
        'set': "⚙️ 設定",
        'instrument': "通貨ペア・銘柄を選択：",
        'err_number': "⚠️ 有効な数字を入力してください（例：1000 または 1850.5）",
        'err_zero_dist': "⚠️ エントリー価格とストップロス価格は同じにできません。もう一度お試しください。",
        'err_state': "⚠️ まず /start を押してください。",
        'err_positive': "⚠️ 値は0より大きくなければなりません。",
    },
}

# Til tugmalari tartibi: 4 ustun x 3 qator, 1-uz, 2-ru, 3-en
LANG_ORDER = [
    'lang_uz', 'lang_ru', 'lang_en', 'lang_tr',
    'lang_ar', 'lang_zh', 'lang_es', 'lang_pt',
    'lang_fr', 'lang_de', 'lang_ko', 'lang_ja',
]

INSTRUMENT_PIPS = {
    "XAUUSD": 10.0, "XAGUSD": 50.0, "BTCUSD": 1.0, "ETHUSD": 1.0,
    "EURUSD": 10.0, "GBPUSD": 10.0, "NAS100": 1.0, "SPX500": 1.0,
}

user_state = {}


def t(chat_id, key):
    """Foydalanuvchining tilidagi matnni qaytaradi, til tanlanmagan bo'lsa default uz."""
    lang_code = user_state.get(chat_id, {}).get('lang', 'lang_uz')
    return LANG[lang_code][key]


def get_lang_kb():
    """Til tanlash uchun inline (shaffof) tugmalar: 4 ustun, 3 qator."""
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(text=LANG[code]['name'], callback_data=code) for code in LANG_ORDER]
    markup.add(*buttons)
    return markup


def get_main_kb(lang_code):
    l = LANG[lang_code]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(l['calc']), types.KeyboardButton(l['contact_btn']))
    markup.add(types.KeyboardButton(l['set']))
    return markup


def get_instrument_kb():
    m = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(i, callback_data=i) for i in INSTRUMENT_PIPS]
    m.add(*buttons)
    return m


def safe_float(text):
    """Matnni floatga aylantiradi, bo'lmasa None qaytaradi (xato chiqarmaydi)."""
    try:
        # vergulni nuqtaga almashtirib ko'ramiz, chunki ba'zi tillarda vergul ishlatiladi
        cleaned = text.strip().replace(',', '.')
        value = float(cleaned)
        return value
    except (ValueError, AttributeError):
        return None


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    user_state[cid] = {}
    bot.send_message(cid, "🌐 Tilni tanlang / Please select your language:", reply_markup=get_lang_kb())


@bot.callback_query_handler(func=lambda call: call.data in LANG_ORDER)
def set_lang(call):
    cid = call.message.chat.id
    user_state[cid] = {'lang': call.data}
    bot.answer_callback_query(call.id)
    bot.send_message(cid, t(cid, 'chosen'), reply_markup=get_main_kb(call.data))


@bot.callback_query_handler(func=lambda call: call.data in INSTRUMENT_PIPS)
def set_inst(call):
    cid = call.message.chat.id
    bot.answer_callback_query(call.id)

    if cid not in user_state or 'lang' not in user_state[cid]:
        bot.send_message(cid, "⚠️ Iltimos, avval /start buyrug'ini bosing.")
        return

    user_state[cid]['inst'] = call.data
    bot.send_message(cid, t(cid, 'bal'))
    bot.register_next_step_handler(call.message, get_balance)


@bot.message_handler(func=lambda message: True)
def menu(message):
    cid = message.chat.id
    if cid not in user_state or 'lang' not in user_state[cid]:
        bot.send_message(cid, "⚠️ Iltimos, avval /start buyrug'ini bosing.")
        return

    l = LANG[user_state[cid]['lang']]

    if message.text == l['calc']:
        bot.send_message(cid, l['instrument'], reply_markup=get_instrument_kb())
    elif message.text == l['contact_btn']:
        bot.send_message(cid, l['contact'])
    elif message.text == l['set']:
        bot.send_message(cid, "🌐 Tilni tanlang / Please select your language:", reply_markup=get_lang_kb())


def get_balance(m):
    cid = m.chat.id
    if cid not in user_state or 'lang' not in user_state[cid]:
        return

    value = safe_float(m.text)
    if value is None or value <= 0:
        bot.send_message(cid, t(cid, 'err_number') if value is None else t(cid, 'err_positive'))
        bot.register_next_step_handler(m, get_balance)
        return

    user_state[cid]['bal'] = value
    bot.send_message(cid, t(cid, 'risk'))
    bot.register_next_step_handler(m, get_risk)


def get_risk(m):
    cid = m.chat.id
    if cid not in user_state or 'lang' not in user_state[cid]:
        return

    value = safe_float(m.text)
    if value is None or value <= 0:
        bot.send_message(cid, t(cid, 'err_number') if value is None else t(cid, 'err_positive'))
        bot.register_next_step_handler(m, get_risk)
        return

    user_state[cid]['risk'] = value
    bot.send_message(cid, t(cid, 'entry'))
    bot.register_next_step_handler(m, get_entry)


def get_entry(m):
    cid = m.chat.id
    if cid not in user_state or 'lang' not in user_state[cid]:
        return

    value = safe_float(m.text)
    if value is None or value <= 0:
        bot.send_message(cid, t(cid, 'err_number') if value is None else t(cid, 'err_positive'))
        bot.register_next_step_handler(m, get_entry)
        return

    user_state[cid]['entry'] = value
    bot.send_message(cid, t(cid, 'sl'))
    bot.register_next_step_handler(m, get_sl)


def get_sl(m):
    cid = m.chat.id
    if cid not in user_state or 'lang' not in user_state[cid]:
        return

    value = safe_float(m.text)
    if value is None or value <= 0:
        bot.send_message(cid, t(cid, 'err_number') if value is None else t(cid, 'err_positive'))
        bot.register_next_step_handler(m, get_sl)
        return

    data = user_state[cid]
    dist = abs(data['entry'] - value)

    if dist == 0:
        bot.send_message(cid, t(cid, 'err_zero_dist'))
        bot.register_next_step_handler(m, get_sl)
        return

    lot = (data['bal'] * (data['risk'] / 100)) / (dist * INSTRUMENT_PIPS[data['inst']])
    bot.send_message(cid, t(cid, 'res').format(inst=data['inst']) + f" {round(lot, 2)}")


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def index():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Bot is running!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
