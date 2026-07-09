import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ቦት ቶከን እና የአድሚን ID እዚህ ያስገቡ
TOKEN = "8874898892:AAFY7QSeTLYFguefCNSVa8tir_inADV5F9E"
ADMIN_ID = 7685177919  # የእርስዎን Telegram ID ይቀይሩ

bot = telebot.TeleBot(TOKEN)

# የቦቱ Settings (በጊዜያዊ ማህደረ ትውስታ ላይ የተቀመጠ)
bot_settings = {
    "force_join": True,
    "channel": "@OSCAR_Q15"
}

# ተጠቃሚው ቻናሉን መቀላቀሉን ማረጋገጫ (Advanced Check)
def is_user_joined(user_id):
    if not bot_settings["force_join"]:
        return True
    try:
        member = bot.get_chat_member(bot_settings["channel"], user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        # ቦቱ ቻናሉ ላይ አድሚን ካልሆነ ወይም ስህተት ከተፈጠረ
        return False

# Start Command
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    if is_user_joined(user_id):
        # ተጠቃሚው ካለቀለ ወይም Force Join ከጠፋ
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("ለመመዝገብ እዚህ ይጫኑ", url="https://t.me/OSCAR_Q15"))
        bot.send_message(
            message.chat.id, 
            "እንኳን ደህና መጡ! ለመመዝገብ ከታች ያለውን ቁልፍ ተጭነው ያናግሩ።", 
            reply_markup=keyboard
        )
    else:
        # ካልተቀላቀለ የሚመጣ
        keyboard = InlineKeyboardMarkup()
        join_btn = InlineKeyboardButton("ቻናሉን ለመቀላቀል", url=f"https://t.me/{bot_settings['channel'].replace('@', '')}")
        check_btn = InlineKeyboardButton("ቼክ አድርግ", callback_data="check_join")
        keyboard.add(join_btn)
        keyboard.add(check_btn)
        
        bot.send_message(
            message.chat.id, 
            f"ቦቱን ለመጠቀም መጀመሪያ የኛን ቻናል መቀላቀል አለብዎት: {bot_settings['channel']}", 
            reply_markup=keyboard
        )

# Admin Panel Command
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        status = "✅ በርቷል" if bot_settings["force_join"] else "❌ ጠፍቷል"
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        add_fj = InlineKeyboardButton("➕ Add ForceJoin", callback_data="admin_add_fj")
        rem_fj = InlineKeyboardButton("➖ Remove ForceJoin", callback_data="admin_rem_fj")
        rem_msg = InlineKeyboardButton("🗑️ Remove Message", callback_data="admin_rem_msg")
        
        keyboard.add(add_fj, rem_fj)
        keyboard.add(rem_msg)
        
        bot.send_message(
            message.chat.id, 
            f"🎛️ **የአድሚን ፓነል**\n\nየForce Join ሁኔታ: {status}\nየአሁኑ ቻናል: {bot_settings['channel']}", 
            parse_mode="Markdown", 
            reply_markup=keyboard
        )
    else:
        bot.send_message(message.chat.id, "❌ ይህንን ትዕዛዝ ለመጠቀም አድሚን አይደሉም።")

# Callback Queries (የአዝራሮች ስራ)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    
    # የተጠቃሚ ቼክ ማድረጊያ አዝራር
    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.answer_callback_query(call.id, "✅ እናመሰግናለን! ተረጋግጧል።")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("ለመመዝገብ እዚህ ይጫኑ", url="https://t.me/OSCAR_Q15"))
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🎉 ስኬታማ! አሁን መመዝገብ ይችላሉ።",
                reply_markup=keyboard
            )
        else:
            bot.answer_callback_query(call.id, "❌ አልተቀላቀሉም! እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ ያድርጉ።", show_alert=True)
            
    # የአድሚን ፓነል አዝራሮች
    elif call.data == "admin_add_fj":
        if user_id == ADMIN_ID:
            bot_settings["force_join"] = True
            bot.answer_callback_query(call.id, "Force Join በርቷል")
            update_admin_msg(call.message)
            
    elif call.data == "admin_rem_fj":
        if user_id == ADMIN_ID:
            bot_settings["force_join"] = False
            bot.answer_callback_query(call.id, "Force Join ጠፍቷል")
            update_admin_msg(call.message)
            
    elif call.data == "admin_rem_msg":
        if user_id == ADMIN_ID:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass

# የአድሚን መልዕክት በየጊዜው አፕዴት ማድረጊያ
def update_admin_msg(message):
    status = "✅ በርቷል" if bot_settings["force_join"] else "❌ ጠፍቷል"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("➕ Add ForceJoin", callback_data="admin_add_fj"), 
                 InlineKeyboardButton("➖ Remove ForceJoin", callback_data="admin_rem_fj"))
    keyboard.add(InlineKeyboardButton("🗑️ Remove Message", callback_data="admin_rem_msg"))
    
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"🎛️ **የአድሚን ፓነል**\n\nየForce Join ሁኔታ: {status}\nየአሁኑ ቻናል: {bot_settings['channel']}",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception:
        pass

# ቦቱን ማስነሻ
if __name__ == '__main__':
    print("ቦቱ በተሳካ ሁኔታ ስራ ጀምሯል...")
    bot.infinity_polling()
