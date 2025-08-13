# app.py
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import imghdr
import threading
import logging
from database import db_init, add_user, is_user_banned, redeem_key, generate_key, is_key_valid, use_premium_key, notify_admin_premium
from config import BOT_TOKEN, ADMIN_ID

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Start command handler
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    add_user(user_id)
    update.message.reply_text("Welcome To Aizen Bot ⚡️\nPlease Use this /redeem Command For Get Prime video 🧑‍💻\nFor Premium use This Command /premium")

# Redeem command handler
def redeem(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    args = context.args

    if is_user_banned(user_id):
        update.message.reply_text("You are banned to use this bot.")
        return

    if not args:
        update.message.reply_text("Please provide a key after /redeem command.")
        return

    key = args[0].strip()

    if redeem_key(user_id):
        # Already redeemed once - free user can redeem only once
        update.message.reply_text("Please Purchase Premium Key For Use 🗝️")
        return

    # Forward redeem message to admin
    bot.send_message(chat_id=ADMIN_ID, text=f"User {user_id} trying to redeem key: {key}")
    update.message.reply_text("Processing 🗝️")

# Premium command handler
def premium(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        update.message.reply_text("You are banned to use this bot.")
        return

    args = context.args
    if not args:
        update.message.reply_text("Please provide a premium key after /premium command.")
        return

    key = args[0].strip()

    if use_premium_key(user_id, key):
        update.message.reply_text("Premium Activated ⚡️")
        notify_admin_premium(user_id)
    else:
        update.message.reply_text("Invalid or already used key!")

# Admin genk command handler
def genk(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    args = context.args
    if not args or not args[0].isdigit():
        update.message.reply_text("Usage: /genk <days>")
        return

    days = int(args[0])
    new_key = generate_key(days)
    update.message.reply_text(f"Generated Premium Key for {days} days:\n{new_key}")

# Add handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('redeem', redeem))
dispatcher.add_handler(CommandHandler('premium', premium))
dispatcher.add_handler(CommandHandler('genk', genk))

# Background thread to run polling bot
def run_bot():
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    db_init()  # initialize db
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=5000)
