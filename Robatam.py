from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
import datetime

TOKEN = '8017078871:AAGZnSaxPFK6WwaZwfzVBXCdegTaJkfAQEY'
ADMIN_ID = 6533580803  # آی‌دی عددی یا یوزرنیم ادمین

bot = Bot(token=TOKEN)

# مراحل گفتگو
CHOOSING, GET_NAME, GET_PHONE, CONFIRM = range(4)

# دیتای موقت هر کاربر
user_data = {}

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("💡 مشاوره", callback_data='مشاوره')],
        [InlineKeyboardButton("🛠 گزارش مشکل", callback_data='مشکل')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("سلام! چه خدمتی نیاز داری؟", reply_markup=reply_markup)
    return CHOOSING

def choose_type(update, context):
    query = update.callback_query
    query.answer()
    user_data[query.from_user.id] = {'type': query.data}
    query.edit_message_text("اسم کوچیکت رو لطفاً بنویس:")
    return GET_NAME

def get_name(update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['name'] = update.message.text.strip()
    update.message.reply_text("شماره تماس رو وارد کن 📞")
    return GET_PHONE

def get_phone(update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['phone'] = update.message.text.strip()

    # ساخت خلاصه اطلاعات
    info = user_data[user_id]
    now = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M")
    info['time'] = now

    text = f"لطفاً تأیید کن 👇\n\n" \
           f"🔹 نوع درخواست: {info['type']}\n" \
           f"👤 نام: {info['name']}\n" \
           f"📞 شماره: {info['phone']}\n" \
           f"⏰ زمان ثبت: {info['time']}"

    keyboard = [
        [InlineKeyboardButton("✅ بله، ارسال کن", callback_data='confirm')],
        [InlineKeyboardButton("🔄 نه، از اول", callback_data='restart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    return CONFIRM

def confirm(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    info = user_data[user_id]

    # ارسال به ادمین
    admin_text = f"📥 فرم جدید ثبت شد:\n\n" \
                 f"🔹 نوع: {info['type']}\n" \
                 f"👤 نام: {info['name']}\n" \
                 f"📞 شماره: {info['phone']}\n" \
                 f"📅 تاریخ: {info['time']}"
    bot.send_message(chat_id=ADMIN_ID, text=admin_text)
    query.edit_message_text("✅ اطلاعاتت ثبت شد! به‌زودی باهات تماس می‌گیریم.")
    return ConversationHandler.END

def restart(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("باشه، بریم از اول...\nاسم کوچیکت رو لطفاً بنویس:")
    return GET_NAME

def cancel(update, context):
    update.message.reply_text("مکالمه لغو شد. هر وقت خواستی /start رو بزن 😊")
    return ConversationHandler.END

# راه‌اندازی ربات
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING: [CallbackQueryHandler(choose_type)],
        GET_NAME: [MessageHandler(Filters.text, get_name)],
        GET_PHONE: [MessageHandler(Filters.text, get_phone)],
        CONFIRM: [
            CallbackQueryHandler(confirm, pattern='confirm'),
            CallbackQueryHandler(restart, pattern='restart')
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

dp.add_handler(conv_handler)

print("🚀 Bot is running...")
updater.start_polling()
updater.idle()