import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# 1. Logging (Crucial for debugging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. Config
TOKEN = "8672169345:AAGAE5R-pbFQteCUkjKM-3DkP5rgp3_fPc4"
POLL_LINK = "https://t.me/c/2800090700/290/19289"

# 3. Flask Web Server (To keep Render happy)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive! 🚀"

def run_flask():
    # Render provides the PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 4. Bot Handlers
async def attendance_reminder_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if used in a group
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups.")
        return

    # Admin Check
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)

    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        await update.message.reply_text("🚫 Only **Admins** can use this.")
        return

    keyboard = [[
        InlineKeyboardButton("✅ Vote Now", url=POLL_LINK),
        InlineKeyboardButton("👍 Already Voted", callback_data="already_voted")
    ]]
    
    await update.message.reply_text(
        "🔔 *ATTENDANCE REMINDER*\n\nPlease mark your attendance for today!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "already_voted":
        await query.message.reply_text(f"🌟 *Great job , {query.from_user.first_name}!*, Thanks for voting", parse_mode='Markdown')

# 5. Main Execution
if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN not found in environment variables!")
        exit(1)

    # Start Flask in a background thread
    Thread(target=run_flask).start()

    # Start Telegram Bot
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('reminder', attendance_reminder_cmd))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot is polling...")
    application.run_polling()
