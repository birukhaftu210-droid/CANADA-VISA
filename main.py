import os
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# ሎግ ማዋቀር
logging.basicConfig(level=logging.INFO)

# ከአካባቢ ተለዋዋጮች (Environment Variables) እሴቶችን ማንበብ
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
CHANNEL = os.environ.get("CHANNEL", "@xpwork2")
REGISTER_URL = os.environ.get("REGISTER_URL", "https://t.me/OSCAR_Q15")
FORCE_JOIN = os.environ.get("FORCE_JOIN", "True").lower() == "true"

if not TOKEN or not ADMIN_ID:
    raise ValueError("BOT_TOKEN እና ADMIN_ID በRender ላይ በEnvironment Variables ውስጥ መገኘት አለባቸው")

bot = telebot.TeleBot(TOKEN)

# 📌 እዚህ ላይ የፎቶዎቹን File ID ያስገቡ (ከላይ ባለው ዘዴ አግኝተው እዚህ ይለጥፉ)
JOB_SECTORS_PHOTO = "AgACAgIAAxkBAAE..."  # 📑 የስራ ዘርፎች ፎቶ ID
BUSINESS_LICENSE_PHOTO = "AgACAgIAAxkBAAE..."  # 🗂 የንግድ ፍቃድ ፎቶ ID

# 🔽 የቁልፎቹ ስሞችን በተለዋዋጮች እንደገና አዋቅሬያለሁ (ትክክለኛ ክፍት ቦታዎችን ይይዛሉ)
BTN_REGISTER = "📝 ለመመዝገብ"
BTN_JOB_SECTORS = "📑 የስራ ዘርፎች"
BTN_BUSINESS_LICENSE = "🗂 የንግድ ፍቃድ"

bot_settings = {
    "force_join": FORCE_JOIN,
    "channel": CHANNEL,
}

app = Flask(__name__)

@app.route('/')
def home():
    return "ቦቱ በሰላም እየሰራ ነው!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def is_user_joined(user_id):
    if not bot_settings["force_join"]:
        return True
    try:
        member = bot.get_chat_member(bot_settings["channel"], user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.warning(f"የአባልነት ማረጋገጫ አልተሳካም ለ {user_id}: {e}")
        return False

def send_join_prompt(chat_id):
    keyboard = InlineKeyboardMarkup()
    join_btn = InlineKeyboardButton("ቻናሉን ለመቀላቀል", url=f"https://t.me/{bot_settings['channel'].replace('@', '')}")
    check_btn = InlineKeyboardButton("ቼክ አድርግ", callback_data="check_join")
    keyboard.add(join_btn, check_btn)
    bot.send_message(
        chat_id,
        f"ቦቱን ለመጠቀም መጀመሪያ የኛን ቻናል መቀላቀል አለብዎት: {bot_settings['channel']}",
        reply_markup=keyboard
    )

# 🔽 እዚህ ላይ ቁልፎቹን በ BTN_... ተለዋዋጮች እየጠቀምኩ አዘጋጅቻለሁ
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton(BTN_REGISTER))
    keyboard.add(KeyboardButton(BTN_JOB_SECTORS), KeyboardButton(BTN_BUSINESS_LICENSE))
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if is_user_joined(user_id):
        keyboard = get_main_keyboard()
        bot.send_message(
            message.chat.id,
            "እንኳን ደህና መጡ! ከታች ካሉት ቁልፎች የሚፈልጉትን ይምረጡ።",
            reply_markup=keyboard
        )
    else:
        send_join_prompt(message.chat.id)

# 🔽 ከዚህ በታች ያሉት አስተናጋጆች በ BTN_... ተለዋዋጮች ትክክለኛውን ፊደል ይጠብቃሉ
@bot.message_handler(func=lambda message: message.text == BTN_REGISTER)
def handle_register_button(message):
    if is_user_joined(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"ለመመዝገብ እባክዎ ይህንን አገናኝ ይጫኑ:\n\n{REGISTER_URL}"
        )
    else:
        send_join_prompt(message.chat.id)

@bot.message_handler(func=lambda message: message.text == BTN_JOB_SECTORS)
def handle_job_sectors(message):
    if is_user_joined(message.from_user.id):
        bot.send_photo(message.chat.id, photo=JOB_SECTORS_PHOTO, caption="📑 የስራ ዘርፎች ዝርዝር ፎቶ")
    else:
        send_join_prompt(message.chat.id)

@bot.message_handler(func=lambda message: message.text == BTN_BUSINESS_LICENSE)
def handle_business_license(message):
    if is_user_joined(message.from_user.id):
        bot.send_photo(message.chat.id, photo=BUSINESS_LICENSE_PHOTO, caption="🗂 የንግድ ፍቃድ ፎቶ")
    else:
        send_join_prompt(message.chat.id)

# 📸 (አማራጭ) ፎቶ ሲልኩ File ID ለማግኘት ከፈለጉ ይህንን መተው ይችላሉ
@bot.message_handler(content_types=['photo'])
def get_photo_id(message):
    file_id = message.photo[-1].file_id
    bot.reply_to(message, f"📸 የፎቶው File ID እነሆ:\n\n`{file_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ ይህንን ትዕዛዝ ለመጠቀም አድሚን አይደሉም።")
        return
    status = "✅ በርቷል" if bot_settings["force_join"] else "❌ ጠፍቷል"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("➕ Add ForceJoin", callback_data="admin_add_fj"),
        InlineKeyboardButton("➖ Remove ForceJoin", callback_data="admin_rem_fj")
    )
    keyboard.add(
        InlineKeyboardButton("🗑️ Remove Message", callback_data="admin_rem_msg")
    )
    bot.send_message(
        message.chat.id,
        f"🎛️ **የአድሚን ፓነል**\n\nየForce Join ሁኔታ: {status}\nየአሁኑ ቻናል: {bot_settings['channel']}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.answer_callback_query(call.id, "✅ እናመሰግናለን! ተረጋግጧል።")
            keyboard = get_main_keyboard()
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="🎉 ስኬታማ! አሁን ከታች ያለውን ቁልፎች ተጭነው መጠቀም ይችላሉ።",
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f"መልእክት ሲሻሻል ስህተት: {e}")
        else:
            bot.answer_callback_query(call.id, "❌ አልተቀላቀሉም! እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ", show_alert=True)
    elif call.data == "admin_add_fj" and user_id == ADMIN_ID:
        bot_settings["force_join"] = True
        bot.answer_callback_query(call.id, "Force Join በርቷል")
        update_admin_msg(call.message)
    elif call.data == "admin_rem_fj" and user_id == ADMIN_ID:
        bot_settings["force_join"] = False
        bot.answer_callback_query(call.id, "Force Join ጠፍቷል")
        update_admin_msg(call.message)
    elif call.data == "admin_rem_msg" and user_id == ADMIN_ID:
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

def update_admin_msg(message):
    status = "✅ በርቷል" if bot_settings["force_join"] else "❌ ጠፍቷል"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("➕ Add ForceJoin", callback_data="admin_add_fj"),
        InlineKeyboardButton("➖ Remove ForceJoin", callback_data="admin_rem_fj")
    )
    keyboard.add(
        InlineKeyboardButton("🗑️ Remove Message", callback_data="admin_rem_msg")
    )
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"🎛️ **የአድሚን ፓነል**\n\nየForce Join ሁኔታ: {status}\nየአሁኑ ቻናል: {bot_settings['channel']}",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except:
        pass

if __name__ == '__main__':
    server_thread = Thread(target=run_flask)
    server_thread.start()
    print("ቦቱ በተሳካ ሁኔታ ስራ ጀምሯል...")
    bot.infinity_polling()
