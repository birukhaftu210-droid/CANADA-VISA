import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import os

# ቦት ቶከን እና የአድሚን ID እዚህ ያስገቡ
TOKEN = "8874898892:AAFY7QSeTLYFguefCNSVa8tir_inADV5F9E"
ADMIN_ID = 7685177919  # የእርስዎን Telegram ID ይቀይሩ

bot = telebot.TeleBot(TOKEN)

# Render እንዳያቋርጠው ፖርት መክፈቻ (Flask App)
app = Flask('')

@app.route('/')
def home():
    return "ቦቱ በሰላም እየሰራ ነው!"

def run_flask():
    # Render የሚሰጠውን ፖርት ይጠቀማል፣ ከሌለ 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# የቦቱ Settings
bot_settings = {
    "force_join": True,
    "channel": "@xpwork2"
}

def is_user_joined(user_id):
    if not bot_settings["force_join"]:
        return True
    try:
        member = bot.get_chat_member(bot_settings["channel"], user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if is_user_joined(user_id):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("ለመመዝገብ እዚህ ይጫኑ", url="https://t.me/OSCAR_Q15"))
        bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ለመመዝገብ ከታች ያለውን ቁልፍ ተጭነው ያናግሩ።", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup()
        join_btn = InlineKeyboardButton("ቻናሉን ለመቀላቀል", url=f"https://t.me/{bot_settings['channel'].replace('@', '')}")
        check_btn = InlineKeyboardButton("ቼክ አድርግ", callback_data="check_join")
        keyboard.add(join_btn, check_btn)
        bot.send_message(message.chat.id, f"ቦቱን ለመጠቀም መጀመሪያ የኛን ቻናል መቀላቀል አለብዎት: {bot_settings['channel']}", reply_markup=keyboard)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        status = "✅ በርቷል" if bot_settings["force_join"] else "❌ ጠፍቷል"
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("➕ Add ForceJoin", callback_data="admin_add_fj"), 
                     InlineKeyboardButton("➖ Remove ForceJoin", callback_data="admin_rem_fj"))
        keyboard.add(InlineKeyboardButton("🗑️ Remove Message", callback_data="admin_rem_msg"))
        bot.send_message(message.chat.id, f"🎛️ **የአድሚን ፓነል**\n\nየForce Join ሁኔታ: {status}\nየአሁኑ ቻናል: {bot_settings['channel']}", parse_mode="Markdown", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "❌ ይህንን ትዕዛዝ ለመጠቀም አድሚን አይደሉም።")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.answer_callback_query(call.id, "✅ እናመሰግናለን! ተረጋግጧል።")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("ለመመዝገብ እዚህ ይጫኑ", url="https://t.me/OSCAR_Q15"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎉 ስኬታማ! አሁን መመዝገብ ይችላሉ።", reply_markup=keyboard)
        else:
            bot.answer_callback_query(call.id, "❌ አልተቀላቀሉም! እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ ያድርጉ።", show_alert=True)
    elif call.data == "admin_add_fj" and user_id == ADMIN_ID:
        bot_settings["force_join"] = True
        bot.answer_callback_query(call.id, "Force Join በርቷል")
        update_admin_msg(call.message)
    elif call.data == "admin_rem_fj" and user_id == ADMIN_ID:
        bot_settings["force_join"] = False
        bot.answer_callback_query(call.id, "Force Join ጠፍቷል")
        update_admin_msg(call.message)
    elif call.data == "admin_rem_msg" and user_id == ADMIN_ID:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass

def update_admin_msg(message):
    status = "✅ በርቷል" if bot_settings["force_join"] else "❌ ጠፍቷል"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("➕ Add ForceJoin", callback_data="admin_add_fj"), InlineKeyboardButton("➖ Remove ForceJoin", callback_data="admin_rem_fj"))
    keyboard.add(InlineKeyboardButton("🗑️ Remove Message", callback_data="admin_rem_msg"))
    try: bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"🎛️ **የአድሚን ፓነል**\n\nየForce Join ሁኔታ: {status}\nየአሁኑ ቻናል: {bot_settings['channel']}", parse_mode="Markdown", reply_markup=keyboard)
    except: pass

if __name__ == '__main__':
    # 1. ዌብሳይቱን በThread (በጀርባ) ያስነሳል
    server_thread = Thread(target=run_flask)
    server_thread.start()
    
    # 2. ቦቱን ያስነሳል
    print("ቦቱ በተሳካ ሁኔታ ስራ ጀምሯል...")
    bot.infinity_polling()
