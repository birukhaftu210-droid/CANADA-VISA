import os
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
CHANNEL = os.environ.get("CHANNEL", "@xpwork2")
REGISTER_URL = os.environ.get("REGISTER_URL", "https://t.me/OSCAR_Q15")
FORCE_JOIN = os.environ.get("FORCE_JOIN", "True").lower() == "true"

if not TOKEN or not ADMIN_ID:
    raise ValueError("BOT_TOKEN እና ADMIN_ID በEnvironment Variables ውስጥ መገኘት አለባቸው")

bot = telebot.TeleBot(TOKEN)

# 📌 አስተካክለነዋል: የፎቶ አይዲዎቹ አሁን በ" " (ኮማ) ውስጥ ገብተዋል!
JOB_SECTORS_PHOTO = "AgACAgQAAxkBAAOmak_-PF-5K-MjwCGPNrmCChM3msIAAukOaxu0OnlSq2jAWcYmQVsBAAMCAAN5AAM8BA"
BUSINESS_LICENSE_PHOTO = "AgACAgQAAxkBAAOqak__ijT2ZJnPECCzXgrRi6Nl6M8AAuwOaxu0OnlSoySaMzAyKLUBAAMCAAN4AAM8BA"

BTN_REGISTER = "📝 ለመመዝገብ"
BTN_JOB_SECTORS = "📑 የስራ ዘርፎች"
BTN_BUSINESS_LICENSE = "🗂 የንግድ ፍቃድ"

bot_settings = {"force_join": FORCE_JOIN, "channel": CHANNEL}
app = Flask(__name__)

@app.route('/')
def home(): return "ቦቱ እየሰራ ነው!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def is_user_joined(user_id):
    if not bot_settings["force_join"]: return True
    try:
        member = bot.get_chat_member(bot_settings["channel"], user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.warning(f"አባልነት አልተረጋገጠም: {e}")
        return False

def send_join_prompt(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("ቻናሉን ለመቀላቀል", url=f"https://t.me/{bot_settings['channel'].replace('@', '')}"),
        InlineKeyboardButton("ቼክ አድርግ", callback_data="check_join")
    )
    bot.send_message(chat_id, f"መጀመሪያ ቻናሉን ቀላቀል: {bot_settings['channel']}", reply_markup=keyboard)

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton(BTN_REGISTER))
    keyboard.add(KeyboardButton(BTN_JOB_SECTORS), KeyboardButton(BTN_BUSINESS_LICENSE))
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    if is_user_joined(message.from_user.id):
        bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ቁልፎቹን ይጫኑ።", reply_markup=get_main_keyboard())
    else:
        send_join_prompt(message.chat.id)

@bot.message_handler(func=lambda m: m.text == BTN_REGISTER)
def handle_register(m):
    if is_user_joined(m.from_user.id):
        bot.send_message(m.chat.id, f"ለመመዝገብ ይህን ይጫኑ:\n\n{REGISTER_URL}")
    else:
        send_join_prompt(m.chat.id)

# 🔽 ፎቶ ካልተጫነ እንኳን ቦቱ እንዳይወድቅ የሚከላከል ክፍል
@bot.message_handler(func=lambda m: m.text == BTN_JOB_SECTORS)
def handle_job_sectors(m):
    if not is_user_joined(m.from_user.id):
        send_join_prompt(m.chat.id); return
    try:
        if JOB_SECTORS_PHOTO:
            bot.send_photo(m.chat.id, photo=JOB_SECTORS_PHOTO, caption="📑 የስራ ዘርፎች ዝርዝር")
        else:
            bot.send_message(m.chat.id, "📑 የስራ ዘርፎች ፎቶ አልተጫነም።")
    except Exception as e:
        bot.send_message(m.chat.id, "ፎቶውን በማውጣት ላይ ችግር ተፈጥሯል።")
        logging.error(f"Job photo error: {e}")

@bot.message_handler(func=lambda m: m.text == BTN_BUSINESS_LICENSE)
def handle_business_license(m):
    if not is_user_joined(m.from_user.id):
        send_join_prompt(m.chat.id); return
    try:
        if BUSINESS_LICENSE_PHOTO:
            bot.send_photo(m.chat.id, photo=BUSINESS_LICENSE_PHOTO, caption="🗂 የንግድ ፍቃድ")
        else:
            bot.send_message(m.chat.id, "🗂 የንግድ ፍቃድ ፎቶ አልተጫነም።")
    except Exception as e:
        bot.send_message(m.chat.id, "ፎቶውን በማውጣት ላይ ችግር ተፈጥሯል።")
        logging.error(f"License photo error: {e}")

# 📸 ይህ ክፍል: ፎቶ ወደ ቦቱ ሲልኩ File ID ን ይመልስልዎታል
@bot.message_handler(content_types=['photo'])
def get_photo_id(message):
    file_id = message.photo[-1].file_id
    bot.reply_to(message, f"✅ የፎቶው File ID እነሆ:\n\n`{file_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ አድሚን ብቻ ነው ይህን የሚጠቀም")
        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("➕ Add ForceJoin", callback_data="admin_add_fj"), 
                 InlineKeyboardButton("➖ Remove ForceJoin", callback_data="admin_rem_fj"))
    keyboard.add(InlineKeyboardButton("🗑️ Remove Message", callback_data="admin_rem_msg"))
    status = "✅ በርቷል" if bot_settings["force_join"] else "❌ ጠፍቷል"
    bot.send_message(message.chat.id, f"**የአድሚን ፓነል**\nForce Join: {status}", parse_mode="Markdown", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "check_join":
        if is_user_joined(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ ተረጋግጧል!")
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="🎉 ስኬታማ! ከታች ያሉትን ቁልፎች ይጫኑ።", reply_markup=get_main_keyboard())
            except: pass
        else:
            bot.answer_callback_query(call.id, "❌ አልተቀላቀሉም!", show_alert=True)
    elif call.data == "admin_add_fj" and call.from_user.id == ADMIN_ID:
        bot_settings["force_join"] = True
        bot.answer_callback_query(call.id, "Force Join በርቷል")
    elif call.data == "admin_rem_fj" and call.from_user.id == ADMIN_ID:
        bot_settings["force_join"] = False
        bot.answer_callback_query(call.id, "Force Join ጠፍቷል")
    elif call.data == "admin_rem_msg" and call.from_user.id == ADMIN_ID:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass

if __name__ == '__main__':
    Thread(target=run_flask).start()
    print("ቦቱ እየሰራ ነው...")
    bot.infinity_polling()
