Import os
import time
import random
import requests
import telebot
from telebot import types
from flask import Flask, request

# --- TOKEN: Environment variable orqali olinadi (xavfsizlik uchun) ---
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable topilmadi! Render Dashboard > Environment bo'limiga qo'shing.")

FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY')

RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://lotpertrade-1.onrender.com')
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Hisoblash tugagandan keyin chiqadigan emoji (random tanlanadi)
CALC_EMOJIS = ["💣", "🏁"]

# --- 12 TA TIL TARJIMASI ---
LANG = {
    'lang_uz': {
        'name': "🇺🇿 O'zbek",
        'chosen': "✅ Til tanlandi: O'zbek",
        'bal': "💰 Keling, hisoblab beraman! Avval balansingizni kiriting (masalan: 1000):",
        'risk': "📊 Ajoyib! Endi risk foizini kiriting (masalan: 2):",
        'entry': "📈 Zo'r! Entry (kirish) narxini kiriting:",
        'sl': "🛑 Yaxshi, endi Stop Loss narxini kiriting:",
        'res': "✅ {inst} uchun lot hajmingiz tayyor:",
        'contact': "📩 Savol yoki taklif bormi? Bemalol yozing: @Shukurillo_M",
        'calc': "🚀 Hisoblash",
        'contact_btn': "📩 Murojaat",
        'set': "⚙️ Sozlamalar",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "Qaysi instrument bo'yicha hisoblaymiz? 👇",
        'err_number': "🤔 Bu raqamga o'xshamadi-ku! Iltimos, faqat son kiriting (masalan: 1000 yoki 1850.5)",
        'err_zero_dist': "⚠️ Entry va Stop Loss narxi bir xil bo'lib qoldi. Birozgina farq bilan qaytadan kiriting 🙂",
        'err_state': "👋 Avval /start buyrug'ini bosing, birga boshlaymiz!",
        'err_positive': "🤔 Qiymat noldan katta bo'lishi kerak. Qaytadan urinib ko'ramizmi?",
        'ask_tp': "🎯 Ajoyib hisoblandi! Take Profit narxini ham kiritib, Risk:Reward nisbatini ko'rib qo'yamizmi?",
        'tp_yes': "✅ Ha, ko'raman",
        'tp_no': "❌ Yo'q, shu yetarli",
        'enter_tp': "🎯 Take Profit narxini kiriting:",
        'rr_great': "🔥 Zo'r nisbat! Bunday savdolar uzoq muddatda yaxshi natija beradi.",
        'rr_good': "💪 Yaxshi nisbat, shu tartibda davom eting!",
        'rr_low': "🙂 Nisbat hozircha pastroq. Imkon bo'lsa, TP'ni biroz uzoqroqqa qo'yishni o'ylab ko'ring.",
        'rr_label': "📐 Risk:Reward nisbati — 1:{rr}",
        'done': "Yana hisoblash uchun \"🚀 Hisoblash\" tugmasini bosing 👇",
        'cal_title': "📅 Shu haftalik muhim (high-impact) yangiliklar — USD, EUR, GBP",
        'cal_loading': "📅 Kalendar yuklanmoqda, biroz kuting...",
        'cal_empty': "📅 Bu hafta USD, EUR, GBP bo'yicha muhim yangilik topilmadi.",
        'cal_error': "⚠️ Kalendarni yuklab bo'lmadi, birozdan keyin qaytadan urinib ko'ring.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
'lang_ru': {
        'name': "🇷🇺 Русский",
        'chosen': "✅ Язык выбран: Русский",
        'bal': "💰 Отлично, начнём! Введите ваш баланс (например: 1000):",
        'risk': "📊 Супер! Теперь введите риск в % (например: 2):",
        'entry': "📈 Хорошо! Введите цену входа (Entry):",
        'sl': "🛑 Принято, теперь введите цену Stop Loss:",
        'res': "✅ Размер лота для {inst} готов:",
        'contact': "📩 Есть вопросы или предложения? Пишите: @Shukurillo_M",
        'calc': "🚀 Рассчитать",
        'contact_btn': "📩 Связь",
        'set': "⚙️ Настройки",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "По какому инструменту считаем? 👇",
        'err_number': "🤔 Это не похоже на число! Введите, пожалуйста, число (например: 1000 или 1850.5)",
        'err_zero_dist': "⚠️ Цены Entry и Stop Loss совпали. Введите немного другое значение 🙂",
        'err_state': "👋 Сначала нажмите /start, начнём вместе!",
        'err_positive': "🤔 Значение должно быть больше нуля. Попробуем снова?",
        'ask_tp': "🎯 Отличный расчёт! Хотите также ввести Take Profit и увидеть Risk:Reward?",
        'tp_yes': "✅ Да, хочу",
        'tp_no': "❌ Нет, этого достаточно",
        'enter_tp': "🎯 Введите цену Take Profit:",
        'rr_great': "🔥 Отличное соотношение! Такие сделки выгодны в долгосрочной перспективе.",
        'rr_good': "💪 Хорошее соотношение, продолжайте в том же духе!",
        'rr_low': "🙂 Соотношение пока низкое. Возможно, стоит увеличить дистанцию до TP.",
        'rr_label': "📐 Соотношение Risk:Reward — 1:{rr}",
        'done': "Хотите посчитать ещё раз? Нажмите \"🚀 Рассчитать\" 👇",
        'cal_title': "📅 Важные новости (high-impact) на этой неделе — USD, EUR, GBP",
        'cal_loading': "📅 Загружаю календарь, подождите...",
        'cal_empty': "📅 На этой неделе важных новостей по USD, EUR, GBP не найдено.",
        'cal_error': "⚠️ Не удалось загрузить календарь, попробуйте позже.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_en': {
        'name': "🇬🇧 English",
        'chosen': "✅ Language selected: English",
        'bal': "💰 Great, let's get started! Enter your balance (e.g. 1000):",
        'risk': "📊 Awesome! Now enter your risk % (e.g. 2):",
        'entry': "📈 Nice! Enter the Entry price:",
        'sl': "🛑 Got it, now enter the Stop Loss price:",
        'res': "✅ Your lot size for {inst} is ready:",
        'contact': "📩 Questions or suggestions? Feel free to message: @Shukurillo_M",
        'calc': "🚀 Calculate",
        'contact_btn': "📩 Contact",
        'set': "⚙️ Settings",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "Which instrument are we calculating for? 👇",
        'err_number': "🤔 That doesn't look like a number! Please enter a valid number (e.g. 1000 or 1850.5)",
        'err_zero_dist': "⚠️ Entry and Stop Loss prices are the same. Please enter a slightly different value 🙂",
        'err_state': "👋 Please press /start first, let's begin together!",
        'err_positive': "🤔 The value must be greater than zero. Shall we try again?",
        'ask_tp': "🎯 Great calculation! Want to also enter Take Profit and see your Risk:Reward ratio?",
        'tp_yes': "✅ Yes, show me",
        'tp_no': "❌ No, that's enough",
        'enter_tp': "🎯 Enter the Take Profit price:",
        'rr_great': "🔥 Excellent ratio! Trades like this pay off in the long run.",
        'rr_good': "💪 Good ratio, keep it up!",
        'rr_low': "🙂 The ratio is a bit low for now. Consider placing your TP a bit further away.",
        'rr_label': "📐 Risk:Reward ratio — 1:{rr}",
        'done': "Want to calculate again? Tap \"🚀 Calculate\" 👇",
        'cal_title': "📅 This week's high-impact news — USD, EUR, GBP",
        'cal_loading': "📅 Loading calendar, please wait...",
        'cal_empty': "📅 No high-impact USD, EUR, GBP news found for this week.",
        'cal_error': "⚠️ Couldn't load the calendar, please try again later.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_tr': {
        'name': "🇹🇷 Türkçe",
        'chosen': "✅ Dil seçildi: Türkçe",
        'bal': "💰 Harika, başlayalım! Bakiyenizi girin (örnek: 1000):",
        'risk': "📊 Süper! Şimdi risk yüzdesini girin (örnek: 2):",
        'entry': "📈 Güzel! Giriş (Entry) fiyatını girin:",
        'sl': "🛑 Anlaşıldı, şimdi Stop Loss fiyatını girin:",
        'res': "✅ {inst} için lot büyüklüğünüz hazır:",
        'contact': "📩 Sorunuz mu var? Yazabilirsiniz: @Shukurillo_M",
        'calc': "🚀 Hesapla",
        'contact_btn': "📩 İletişim",
        'set': "⚙️ Ayarlar",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "Hangi enstrüman için hesaplayalım? 👇",
        'err_number': "🤔 Bu bir sayıya benzemiyor! Lütfen geçerli bir sayı girin (örnek: 1000 veya 1850.5)",
        'err_zero_dist': "⚠️ Entry ve Stop Loss fiyatları aynı oldu. Lütfen biraz farklı bir değer girin 🙂",
        'err_state': "👋 Önce /start komutunu çalıştırın, birlikte başlayalım!",
        'err_positive': "🤔 Değer sıfırdan büyük olmalı. Tekrar deneyelim mi?",
        'ask_tp': "🎯 Harika hesaplandı! Take Profit girip Risk:Reward oranını da görmek ister misiniz?",
        'tp_yes': "✅ Evet, göster",
        'tp_no': "❌ Hayır, bu yeterli",
        'enter_tp': "🎯 Take Profit fiyatını girin:",
        'rr_great': "🔥 Mükemmel oran! Böyle işlemler uzun vadede kazandırır.",
        'rr_good': "💪 İyi bir oran, böyle devam edin!",
        'rr_low': "🙂 Oran şimdilik biraz düşük. TP'yi biraz daha uzağa koymayı düşünebilirsiniz.",
        'rr_label': "📐 Risk:Reward oranı — 1:{rr}",
        'done': "Tekrar hesaplamak için \"🚀 Hesapla\" butonuna basın 👇",
        'cal_title': "📅 Bu haftanın önemli (high-impact) haberleri — USD, EUR, GBP",
        'cal_loading': "📅 Takvim yükleniyor, lütfen bekleyin...",
        'cal_empty': "📅 Bu hafta USD, EUR, GBP için önemli haber bulunamadı.",
        'cal_error': "⚠️ Takvim yüklenemedi, lütfen daha sonra tekrar deneyin.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_ar': {
        'name': "🇸🇦 العربية",
        'chosen': "✅ تم اختيار اللغة: العربية",
        'bal': "💰 رائع، لنبدأ! أدخل رصيدك (مثال: 1000):",
        'risk': "📊 ممتاز! الآن أدخل نسبة المخاطرة % (مثال: 2):",
        'entry': "📈 جيد! أدخل سعر الدخول (Entry):",
        'sl': "🛑 تم، الآن أدخل سعر وقف الخسارة (Stop Loss):",
        'res': "✅ حجم اللوت لـ {inst} جاهز:",
        'contact': "📩 لديك سؤال؟ تواصل معنا: @Shukurillo_M",
        'calc': "🚀 احساب",
        'contact_btn': "📩 تواصل",
        'set': "⚙️ الإعدادات",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "لأي أداة نحسب؟ 👇",
        'err_number': "🤔 هذا لا يشبه رقمًا! يرجى إدخال رقم صحيح (مثال: 1000 أو 1850.5)",
        'err_zero_dist': "⚠️ سعر الدخول وسعر وقف الخسارة متطابقان. أدخل قيمة مختلفة قليلاً 🙂",
        'err_state': "👋 يرجى الضغط على /start أولاً، لنبدأ معًا!",
        'err_positive': "🤔 يجب أن تكون القيمة أكبر من الصفر. هل نحاول مرة أخرى؟",
        'ask_tp': "🎯 حساب رائع! هل تريد إدخال Take Profit ورؤية نسبة Risk:Reward؟",
        'tp_yes': "✅ نعم، أرني",
        'tp_no': "❌ لا، هذا يكفي",
        'enter_tp': "🎯 أدخل سعر Take Profit:",
        'rr_great': "🔥 نسبة رائعة! مثل هذه الصفقات تحقق نتائج جيدة على المدى الطويل.",
        'rr_good': "💪 نسبة جيدة، استمر على هذا النحو!",
        'rr_low': "🙂 النسبة منخفضة حاليًا. فكر في وضع TP بعيدًا أكثر.",
        'rr_label': "📐 نسبة Risk:Reward — 1:{rr}",
        'done': "هل تريد الحساب مرة أخرى؟ اضغط \"🚀 احساب\" 👇",
        'cal_title': "📅 أخبار هذا الأسبوع المهمة (high-impact) — USD, EUR, GBP",
        'cal_loading': "📅 جاري تحميل التقويم، يرجى الانتظار...",
        'cal_empty': "📅 لم يتم العثور على أخبار مهمة لـ USD, EUR, GBP هذا الأسبوع.",
        'cal_error': "⚠️ تعذر تحميل التقويم، يرجى المحاولة مرة أخرى لاحقًا.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_zh': {
        'name': "🇨🇳 中文",
        'chosen': "✅ 已选择语言：中文",
        'bal': "💰 太好了，我们开始吧！请输入余额（例如：1000）：",
        'risk': "📊 很好！现在请输入风险百分比（例如：2）：",
        'entry': "📈 不错！请输入入场价格（Entry）：",
        'sl': "🛑 好的，现在请输入止损价格（Stop Loss）：",
        'res': "✅ {inst} 的手数已计算好：",
        'contact': "📩 有问题或建议？请联系：@Shukurillo_M",
        'calc': "🚀 计算",
        'contact_btn': "📩 联系",
        'set': "⚙️ 设置",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "我们要为哪个品种计算？👇",
        'err_number': "🤔 这不像是个数字！请输入有效数字（例如：1000 或 1850.5）",
        'err_zero_dist': "⚠️ 入场价和止损价相同了，请输入稍微不同的数值 🙂",
        'err_state': "👋 请先点击 /start，我们一起开始吧！",
        'err_positive': "🤔 数值必须大于零，再试一次吧？",
        'ask_tp': "🎯 计算完成！想输入止盈（Take Profit）并查看风险回报比吗？",
        'tp_yes': "✅ 好的，显示一下",
        'tp_no': "❌ 不用了，这样就够了",
        'enter_tp': "🎯 请输入止盈（Take Profit）价格：",
        'rr_great': "🔥 非常棒的比例！这样的交易长期来看很有价值。",
        'rr_good': "💪 不错的比例，继续保持！",
        'rr_low': "🙂 目前比例有点低，可以考虑把止盈设得更远一些。",
        'rr_label': "📐 风险回报比 — 1:{rr}",
        'done': "还想再计算一次吗？点击 \"🚀 计算\" 👇",
        'cal_title': "📅 本周重要（高影响）新闻 — USD, EUR, GBP",
        'cal_loading': "📅 正在加载日历，请稍候...",
        'cal_empty': "📅 本周未找到 USD, EUR, GBP 的重要新闻。",
        'cal_error': "⚠️ 无法加载日历，请稍后再试。",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_es': {
        'name': "🇪🇸 Español",
        'chosen': "✅ Idioma seleccionado: Español",
        'bal': "💰 ¡Genial, comencemos! Ingrese su balance (ej: 1000):",
        'risk': "📊 ¡Perfecto! Ahora ingrese el % de riesgo (ej: 2):",
        'entry': "📈 ¡Bien! Ingrese el precio de entrada (Entry):",
        'sl': "🛑 Listo, ahora ingrese el precio de Stop Loss:",
        'res': "✅ Su tamaño de lote para {inst} está listo:",
        'contact': "📩 ¿Preguntas o sugerencias? Escriba: @Shukurillo_M",
        'calc': "🚀 Calcular",
        'contact_btn': "📩 Contacto",
        'set': "⚙️ Ajustes",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "¿Para qué instrumento calculamos? 👇",
        'err_number': "🤔 Eso no parece un número. Por favor ingrese un número válido (ej: 1000 o 1850.5)",
        'err_zero_dist': "⚠️ Los precios de Entry y Stop Loss son iguales. Ingrese un valor un poco diferente 🙂",
        'err_state': "👋 Presione /start primero, ¡empecemos juntos!",
        'err_positive': "🤔 El valor debe ser mayor que cero. ¿Intentamos de nuevo?",
        'ask_tp': "🎯 ¡Excelente cálculo! ¿Quiere ingresar también el Take Profit y ver su ratio Risk:Reward?",
        'tp_yes': "✅ Sí, muéstramelo",
        'tp_no': "❌ No, es suficiente",
        'enter_tp': "🎯 Ingrese el precio de Take Profit:",
        'rr_great': "🔥 ¡Excelente ratio! Este tipo de operaciones rinden a largo plazo.",
        'rr_good': "💪 Buen ratio, ¡sigue así!",
        'rr_low': "🙂 El ratio es un poco bajo por ahora. Considere colocar el TP un poco más lejos.",
        'rr_label': "📐 Ratio Risk:Reward — 1:{rr}",
        'done': "¿Quiere calcular de nuevo? Toque \"🚀 Calcular\" 👇",
        'cal_title': "📅 Noticias de alto impacto de esta semana — USD, EUR, GBP",
        'cal_loading': "📅 Cargando calendario, espere por favor...",
        'cal_empty': "📅 No se encontraron noticias de alto impacto para USD, EUR, GBP esta semana.",
        'cal_error': "⚠️ No se pudo cargar el calendario, intente de nuevo más tarde.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_pt': {
        'name': "🇵🇹 Português",
        'chosen': "✅ Idioma selecionado: Português",
        'bal': "💰 Ótimo, vamos começar! Insira seu saldo (ex: 1000):",
        'risk': "📊 Perfeito! Agora insira o % de risco (ex: 2):",
        'entry': "📈 Bom! Insira o preço de entrada (Entry):",
        'sl': "🛑 Certo, agora insira o preço de Stop Loss:",
        'res': "✅ Seu tamanho de lote para {inst} está pronto:",
        'contact': "📩 Perguntas ou sugestões? Escreva: @Shukurillo_M",
        'calc': "🚀 Calcular",
        'contact_btn': "📩 Contato",
        'set': "⚙️ Configurações",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "Para qual instrumento vamos calcular? 👇",
        'err_number': "🤔 Isso não parece um número. Insira um número válido (ex: 1000 ou 1850.5)",
        'err_zero_dist': "⚠️ Os preços de Entry e Stop Loss ficaram iguais. Insira um valor um pouco diferente 🙂",
        'err_state': "👋 Pressione /start primeiro, vamos começar juntos!",
        'err_positive': "🤔 O valor deve ser maior que zero. Vamos tentar de novo?",
        'ask_tp': "🎯 Ótimo cálculo! Quer inserir também o Take Profit e ver seu ratio Risk:Reward?",
        'tp_yes': "✅ Sim, mostrar",
        'tp_no': "❌ Não, já chega",
        'enter_tp': "🎯 Insira o preço de Take Profit:",
        'rr_great': "🔥 Excelente ratio! Esse tipo de operação compensa a longo prazo.",
        'rr_good': "💪 Bom ratio, continue assim!",
        'rr_low': "🙂 O ratio está um pouco baixo por agora. Considere colocar o TP um pouco mais distante.",
        'rr_label': "📐 Ratio Risk:Reward — 1:{rr}",
        'done': "Quer calcular novamente? Toque em \"🚀 Calcular\" 👇",
        'cal_title': "📅 Notícias de alto impacto desta semana — USD, EUR, GBP",
        'cal_loading': "📅 Carregando calendário, aguarde...",
        'cal_empty': "📅 Nenhuma notícia de alto impacto encontrada para USD, EUR, GBP esta semana.",
        'cal_error': "⚠️ Não foi possível carregar o calendário, tente novamente mais tarde.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_fr': {
        'name': "🇫🇷 Français",
        'chosen': "✅ Langue sélectionnée : Français",
        'bal': "💰 Parfait, commençons ! Entrez votre solde (ex: 1000):",
        'risk': "📊 Super ! Entrez maintenant le % de risque (ex: 2):",
        'entry': "📈 Bien ! Entrez le prix d'entrée (Entry):",
        'sl': "🛑 Noté, entrez maintenant le prix du Stop Loss:",
        'res': "✅ Votre taille de lot pour {inst} est prête:",
        'contact': "📩 Des questions ? Écrivez-nous : @Shukurillo_M",
        'calc': "🚀 Calculer",
        'contact_btn': "📩 Contact",
        'set': "⚙️ Paramètres",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "Pour quel instrument calculons-nous ? 👇",
        'err_number': "🤔 Cela ne ressemble pas à un nombre ! Entrez un nombre valide (ex: 1000 ou 1850.5)",
        'err_zero_dist': "⚠️ Les prix Entry et Stop Loss sont identiques. Entrez une valeur légèrement différente 🙂",
        'err_state': "👋 Appuyez d'abord sur /start, commençons ensemble !",
        'err_positive': "🤔 La valeur doit être supérieure à zéro. On réessaie ?",
        'ask_tp': "🎯 Excellent calcul ! Voulez-vous aussi entrer le Take Profit et voir votre ratio Risk:Reward ?",
        'tp_yes': "✅ Oui, montrez-moi",
        'tp_no': "❌ Non, ça suffit",
        'enter_tp': "🎯 Entrez le prix du Take Profit:",
        'rr_great': "🔥 Excellent ratio ! Ce type de trade est payant sur le long terme.",
        'rr_good': "💪 Bon ratio, continuez comme ça !",
        'rr_low': "🙂 Le ratio est un peu faible pour l'instant. Pensez à placer le TP un peu plus loin.",
        'rr_label': "📐 Ratio Risk:Reward — 1:{rr}",
        'done': "Vous voulez recalculer ? Appuyez sur \"🚀 Calculer\" 👇",
        'cal_title': "📅 Actualités à fort impact de cette semaine — USD, EUR, GBP",
        'cal_loading': "📅 Chargement du calendrier, veuillez patienter...",
        'cal_empty': "📅 Aucune actualité à fort impact trouvée pour USD, EUR, GBP cette semaine.",
        'cal_error': "⚠️ Impossible de charger le calendrier, veuillez réessayer plus tard.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_de': {
        'name': "🇩🇪 Deutsch",
        'chosen': "✅ Sprache ausgewählt: Deutsch",
        'bal': "💰 Super, legen wir los! Geben Sie Ihr Guthaben ein (z.B. 1000):",
        'risk': "📊 Klasse! Geben Sie jetzt das Risiko in % ein (z.B. 2):",
        'entry': "📈 Gut! Geben Sie den Einstiegspreis (Entry) ein:",
        'sl': "🛑 Verstanden, geben Sie jetzt den Stop-Loss-Preis ein:",
        'res': "✅ Ihre Lotgröße für {inst} ist fertig:",
        'contact': "📩 Fragen oder Vorschläge? Schreiben Sie: @Shukurillo_M",
        'calc': "🚀 Berechnen",
        'contact_btn': "📩 Kontakt",
        'set': "⚙️ Einstellungen",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "Für welches Instrument berechnen wir? 👇",
        'err_number': "🤔 Das sieht nicht nach einer Zahl aus! Bitte geben Sie eine gültige Zahl ein (z.B. 1000 oder 1850.5)",
        'err_zero_dist': "⚠️ Entry- und Stop-Loss-Preis sind gleich. Geben Sie bitte einen etwas anderen Wert ein 🙂",
        'err_state': "👋 Bitte drücken Sie zuerst /start, lassen Sie uns gemeinsam starten!",
        'err_positive': "🤔 Der Wert muss größer als null sein. Versuchen wir es noch einmal?",
        'ask_tp': "🎯 Tolle Berechnung! Möchten Sie auch den Take Profit eingeben und Ihr Risk:Reward-Verhältnis sehen?",
        'tp_yes': "✅ Ja, zeigen",
        'tp_no': "❌ Nein, das reicht",
        'enter_tp': "🎯 Geben Sie den Take-Profit-Preis ein:",
        'rr_great': "🔥 Hervorragendes Verhältnis! Solche Trades zahlen sich langfristig aus.",
        'rr_good': "💪 Gutes Verhältnis, weiter so!",
        'rr_low': "🙂 Das Verhältnis ist momentan etwas niedrig. Überlegen Sie, den TP etwas weiter zu setzen.",
        'rr_label': "📐 Risk:Reward-Verhältnis — 1:{rr}",
        'done': "Nochmal berechnen? Tippen Sie auf \"🚀 Berechnen\" 👇",
        'cal_title': "📅 Wichtige Nachrichten dieser Woche (High-Impact) — USD, EUR, GBP",
        'cal_loading': "📅 Kalender wird geladen, bitte warten...",
        'cal_empty': "📅 Keine High-Impact-Nachrichten für USD, EUR, GBP diese Woche gefunden.",
        'cal_error': "⚠️ Kalender konnte nicht geladen werden, bitte versuchen Sie es später erneut.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_ko': {
        'name': "🇰🇷 한국어",
        'chosen': "✅ 언어가 선택되었습니다: 한국어",
        'bal': "💰 좋아요, 시작해볼까요! 잔액을 입력하세요 (예: 1000):",
        'risk': "📊 좋습니다! 이제 리스크 %를 입력하세요 (예: 2):",
        'entry': "📈 좋아요! 진입가(Entry)를 입력하세요:",
        'sl': "🛑 알겠습니다, 이제 손절가(Stop Loss)를 입력하세요:",
        'res': "✅ {inst}의 로트 크기가 준비되었습니다:",
        'contact': "📩 질문이나 제안이 있으신가요? 연락주세요: @Shukurillo_M",
        'calc': "🚀 계산하기",
        'contact_btn': "📩 문의",
        'set': "⚙️ 설정",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "어떤 상품으로 계산할까요? 👇",
        'err_number': "🤔 숫자가 아닌 것 같아요! 올바른 숫자를 입력해주세요 (예: 1000 또는 1850.5)",
        'err_zero_dist': "⚠️ 진입가와 손절가가 같습니다. 조금 다른 값을 입력해주세요 🙂",
        'err_state': "👋 먼저 /start를 눌러주세요, 함께 시작해봐요!",
        'err_positive': "🤔 값은 0보다 커야 합니다. 다시 시도해볼까요?",
        'ask_tp': "🎯 계산 완료! Take Profit도 입력해서 Risk:Reward 비율을 확인해보시겠어요?",
        'tp_yes': "✅ 네, 보여주세요",
        'tp_no': "❌ 아니요, 충분해요",
        'enter_tp': "🎯 Take Profit 가격을 입력하세요:",
        'rr_great': "🔥 훌륭한 비율이에요! 이런 거래는 장기적으로 좋은 결과를 가져옵니다.",
        'rr_good': "💪 좋은 비율이에요, 계속 이렇게 해보세요!",
        'rr_low': "🙂 비율이 조금 낮네요. TP를 조금 더 멀리 설정하는 것도 고려해보세요.",
        'rr_label': "📐 Risk:Reward 비율 — 1:{rr}",
        'done': "다시 계산하고 싶으신가요? \"🚀 계산하기\"를 눌러주세요 👇",
        'cal_title': "📅 이번 주 고영향(high-impact) 뉴스 — USD, EUR, GBP",
        'cal_loading': "📅 캘린더를 불러오는 중입니다, 잠시 기다려주세요...",
        'cal_empty': "📅 이번 주 USD, EUR, GBP 관련 고영향 뉴스가 없습니다.",
        'cal_error': "⚠️ 캘린더를 불러올 수 없습니다. 나중에 다시 시도해주세요.",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
    'lang_ja': {
        'name': "🇯🇵 日本語",
        'chosen': "✅ 言語が選択されました：日本語",
        'bal': "💰 いいですね、始めましょう！残高を入力してください（例：1000）：",
        'risk': "📊 完璧です！次にリスク％を入力してください（例：2）：",
        'entry': "📈 いいですね！エントリー価格を入力してください：",
        'sl': "🛑 了解です、次にストップロス価格を入力してください：",
        'res': "✅ {inst} のロットサイズが準備できました：",
        'contact': "📩 ご質問やご提案がありますか？お気軽にご連絡ください：@Shukurillo_M",
        'calc': "🚀 計算する",
        'contact_btn': "📩 連絡先",
        'set': "⚙️ 設定",
        'calendar_btn': "📅 Economic Calendar",
        'instrument': "どの銘柄で計算しますか？👇",
        'err_number': "🤔 数字には見えませんね！有効な数字を入力してください（例：1000 または 1850.5）",
        'err_zero_dist': "⚠️ エントリー価格とストップロス価格が同じです。少し異なる値を入力してください 🙂",
        'err_state': "👋 まず /start を押してください、一緒に始めましょう！",
        'err_positive': "🤔 値は0より大きくなければなりません。もう一度試しますか？",
        'ask_tp': "🎯 計算完了！Take Profitも入力してRisk:Reward比率を見てみますか？",
        'tp_yes': "✅ はい、見せてください",
        'tp_no': "❌ いいえ、これで十分です",
        'enter_tp': "🎯 Take Profitの価格を入力してください：",
        'rr_great': "🔥 素晴らしい比率です！このようなトレードは長期的に良い結果をもたらします。",
        'rr_good': "💪 良い比率ですね、このまま続けましょう！",
        'rr_low': "🙂 比率は今のところ少し低めです。TPをもう少し遠くに設定することを検討してみてください。",
        'rr_label': "📐 Risk:Reward比率 — 1:{rr}",
        'done': "もう一度計算しますか？「🚀 計算する」をタップしてください 👇",
        'cal_title': "📅 今週の重要（高インパクト）ニュース — USD, EUR, GBP",
        'cal_loading': "📅 カレンダーを読み込んでいます、お待ちください...",
        'cal_empty': "📅 今週のUSD, EUR, GBPに関する重要ニュースは見つかりませんでした。",
        'cal_error': "⚠️ カレンダーを読み込めませんでした、後でもう一度お試しください。",
        'cal_item': "🔴 {date} {time} | {country} | {event}",
    },
}

# Til tugmalari tartibi: 4 ustun x 3 qator, 1-uz, 2-ru, 3-en
LANG_ORDER = [
    'lang_uz', 'lang_ru', 'lang_en', 'lang_tr',
    'lang_ar', 'lang_zh', 'lang_es', 'lang_pt',
    'lang_fr', 'lang_de', 'lang_ko', 'lang_ja',
]

# Har bir instrumentning 1 standart lot hajmi (contract size).
# Lot = (Balans * Risk%) / (Entry-SL masofasi * Contract_size)
INSTRUMENT_CONTRACT_SIZE = {
    "XAUUSD": 100,      # 1 lot = 100 untsiya oltin
    "XAGUSD": 5000,     # 1 lot = 5000 untsiya kumush
    "BTCUSD": 1,        # 1 lot = 1 BTC
    "ETHUSD": 1,        # 1 lot = 1 ETH
    "EURUSD": 100000,   # 1 lot = 100,000 EUR
    "GBPUSD": 100000,   # 1 lot = 100,000 GBP
    "NAS100": 1,        # 1 lot = 1 kontrakt (broker'ga qarab farq qilishi mumkin)
    "SPX500": 1,        # 1 lot = 1 kontrakt (broker'ga qarab farq qilishi mumkin)
}

# Economic Calendar uchun kuzatiladigan valyutalar
WATCHED_CURRENCIES = {"USD", "EUR", "GBP"}

user_state = {}

# Economic calendar keshi: {"data": [...], "fetched_at": datetime}
calendar_cache = {"data": None, "fetched_at": None}
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 soat


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
    markup.add(types.KeyboardButton(l['calendar_btn']))
    markup.add(types.KeyboardButton(l['set']))
    return markup


def get_instrument_kb():
    m = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(i, callback_data=i) for i in INSTRUMENT_CONTRACT_SIZE]
    m.add(*buttons)
    return m


def get_tp_kb(lang_code):
    l = LANG[lang_code]
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(l['tp_yes'], callback_data='tp_yes'),
        types.InlineKeyboardButton(l['tp_no'], callback_data='tp_no'),
    )
    return m


def safe_float(text):
    """Matnni floatga aylantiradi, bo'lmasa None qaytaradi (xato chiqarmaydi)."""
    try:
        cleaned = text.strip().replace(',', '.')
        value = float(cleaned)
        return value
    except (ValueError, AttributeError, TypeError):
        return None


def send_calc_emoji(chat_id):
    """Hisoblash tugashidan oldin random emoji yuboradi va 1 soniya kutadi."""
    emoji = random.choice(CALC_EMOJIS)
    bot.send_message(chat_id, emoji)
    time.sleep(1)


def send_lot_result(chat_id, lang_code, with_done_text=True):
    """Lot natijasini chiqaradi."""
    l = LANG[lang_code]
    data = user_state[chat_id]
    bot.send_message(chat_id, l['res'].format(inst=data['inst']) + f" *{round(data['lot'], 2)}*", parse_mode="Markdown")
    if with_done_text:
        bot.send_message(chat_id, l['done'])


def fetch_economic_calendar():
    """
    Finnhub API orqali shu haftalik economic calendar ma'lumotini oladi.
    Faqat USD, EUR, GBP uchun high-impact yangiliklarni qaytaradi.
    Natija 24 soat davomida xotirada (kesh) saqlanadi, qayta so'rov yuborilmaydi.
    """
    from datetime import datetime, timedelta

    now = datetime.utcnow()

    # Agar kesh hali yangi bo'lsa (24 soatdan kam vaqt o'tgan bo'lsa), saqlangan ma'lumotni qaytaramiz
    if calendar_cache["data"] is not None and calendar_cache["fetched_at"] is not None:
        age = (now - calendar_cache["fetched_at"]).total_seconds()
        if age < CACHE_TTL_SECONDS:
            return calendar_cache["data"]

    if not FINNHUB_API_KEY:
        return None

    from_date = now.strftime("%Y-%m-%d")
    to_date = (now + timedelta(days=7)).strftime("%Y-%m-%d")

    url = "https://finnhub.io/api/v1/calendar/economic"
    params = {"from": from_date, "to": to_date, "token": FINNHUB_API_KEY}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        raw_events = payload.get("economicCalendar", []) or []
    except Exception:
        # Tarmoq xatosi yoki API ishlamasa, eski keshni (agar bor bo'lsa) qaytaramiz, aks holda None
        return calendar_cache["data"]

    filtered = []
    for ev in raw_events:
        impact = str(ev.get("impact", "")).lower()
        country_code = str(ev.get("country", "")).upper()

        if impact != "high":
            continue
        if country_code not in WATCHED_CURRENCIES:
            continue

        filtered.append({
            "datetime": ev.get("time", ""),
            "country": country_code,
            "event": ev.get("event", "—"),
        })

    # Sana bo'yicha tartiblash
    filtered.sort(key=lambda x: x["datetime"])

    calendar_cache["data"] = filtered
    calendar_cache["fetched_at"] = now

    return filtered


def format_calendar_message(events, lang_code):
    """Calendar hodisalarini foydalanuvchi tiliga mos matn ko'rinishiga formatlaydi."""
    l = LANG[lang_code]

    if events is None:
        return l['cal_error']

    if len(events) == 0:
        return l['cal_empty']

    lines = [l['cal_title'], ""]
    for ev in events:
        dt_str = ev["datetime"]
        date_part, time_part = "", ""
        if " " in dt_str:
            date_part, time_part = dt_str.split(" ", 1)
        else:
            date_part = dt_str

        line = l['cal_item'].format(
            date=date_part,
            time=time_part,
            country=ev["country"],
            event=ev["event"],
        )
        lines.append(line)

    return "\n".join(lines)


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


@bot.callback_query_handler(func=lambda call: call.data in INSTRUMENT_CONTRACT_SIZE)
def set_inst(call):
    cid = call.message.chat.id
    bot.answer_callback_query(call.id)

    if cid not in user_state or 'lang' not in user_state[cid]:
        bot.send_message(cid, "👋 Avval /start buyrug'ini bosing, birga boshlaymiz!")
        return

    user_state[cid]['inst'] = call.data
    bot.send_message(cid, t(cid, 'bal'))
    bot.register_next_step_handler(call.message, get_balance)


@bot.callback_query_handler(func=lambda call: call.data in ('tp_yes', 'tp_no'))
def handle_tp_choice(call):
    cid = call.message.chat.id
    bot.answer_callback_query(call.id)

    if cid not in user_state or 'lang' not in user_state[cid]:
        bot.send_message(cid, "👋 Avval /start buyrug'ini bosing, birga boshlaymiz!")
        return

    lang_code = user_state[cid]['lang']

    if call.data == 'tp_no':
        send_calc_emoji(cid)
        send_lot_result(cid, lang_code)
    else:
        bot.send_message(cid, t(cid, 'enter_tp'))
        bot.register_next_step_handler(call.message, get_tp)


@bot.message_handler(func=lambda message: True)
def menu(message):
    cid = message.chat.id
    if cid not in user_state or 'lang' not in user_state[cid]:
        bot.send_message(cid, "👋 Avval /start buyrug'ini bosing, birga boshlaymiz!")
        return

    l = LANG[user_state[cid]['lang']]

    if message.text == l['calc']:
        bot.send_message(cid, l['instrument'], reply_markup=get_instrument_kb())
    elif message.text == l['contact_btn']:
        bot.send_message(cid, l['contact'])
    elif message.text == l['calendar_btn']:
        bot.send_message(cid, l['cal_loading'])
        events = fetch_economic_calendar()
        msg = format_calendar_message(events, user_state[cid]['lang'])
        bot.send_message(cid, msg)
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

    data['sl'] = value
    lot = (data['bal'] * (data['risk'] / 100)) / (dist * INSTRUMENT_CONTRACT_SIZE[data['inst']])
    data['lot'] = lot

    lang_code = data['lang']
    bot.send_message(cid, t(cid, 'ask_tp'), reply_markup=get_tp_kb(lang_code))


def get_tp(m):
    cid = m.chat.id
    if cid not in user_state or 'lang' not in user_state[cid]:
        return

    value = safe_float(m.text)
    if value is None or value <= 0:
        bot.send_message(cid, t(cid, 'err_number') if value is None else t(cid, 'err_positive'))
        bot.register_next_step_handler(m, get_tp)
        return

    data = user_state[cid]
    lang_code = data['lang']

    risk_dist = abs(data['entry'] - data['sl'])
    reward_dist = abs(value - data['entry'])

    if reward_dist == 0:
        bot.send_message(cid, t(cid, 'err_zero_dist'))
        bot.register_next_step_handler(m, get_tp)
        return

    rr = round(reward_dist / risk_dist, 2)

    send_calc_emoji(cid)
    send_lot_result(cid, lang_code, with_done_text=False)

    l = LANG[lang_code]
    if rr >= 3:
        feeling = l['rr_great']
    elif rr >= 1.5:
        feeling = l['rr_good']
    else:
        feeling = l['rr_low']

    bot.send_message(cid, l['rr_label'].format(rr=rr) + "\n" + feeling)
    bot.send_message(cid, l['done'])


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
    # Ping kelganda, agar kesh eskirgan bo'lsa, economic calendar'ni fonda yangilab qo'yamiz
    try:
        fetch_economic_calendar()
    except Exception:
        pass
    return "Bot is running!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
