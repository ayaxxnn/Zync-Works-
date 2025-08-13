from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters
from database import add_user, is_user_banned, redeem_key, is_premium, use_premium_key, generate_key, ban_user, unban_user, get_all_users
from config import ADMIN_ID
import logging

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    add_user(user_id)
    update.message.reply_text(
        "Welcome To Aizen Bot ⚡️\n"
        "Please Use this /redeem Command For Get Prime video 🧑‍💻\n"
        "For Premium use This Command /premium"
    )

def redeem(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    args = context.args

    if is_user_banned(user_id):
        update.message.reply_text("You are banned to use this bot.")
        return

    if not args:
        update.message.reply_text("Please send the redeem key after /redeem command.")
        return

    if redeem_key(user_id):
        # User already redeemed free key earlier
        update.message.reply_text("Please Purchase Premium Key For Use 🗝️")
        return

    key = args[0].strip()
    # Forward redeem message to admin
    context.bot.send_message(chat_id=ADMIN_ID, text=f"User {user_id} Requested Redeem key: {key}")
    update.message.reply_text("Processing 🗝️")

def premium(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    args = context.args

    if is_user_banned(user_id):
        update.message.reply_text("You are banned to use this bot.")
        return

    if not args:
        update.message.reply_text("Please send your premium key after /premium command.")
        return

    key = args[0].strip()
    if use_premium_key(user_id, key):
        update.message.reply_text("Premium Activated ⚡️")
        # Notify admin
        context.bot.send_message(chat_id=ADMIN_ID, text=f"User {user_id} Activated Premium with key {key}")
    else:
        update.message.reply_text("Invalid or already used premium key!")

def genk(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("Only admin can use this command.")
        return

    args = context.args
    if not args or not args[0].isdigit():
        update.message.reply_text("Usage: /genk <days>")
        return

    days = int(args[0])
    key = generate_key(days)
    update.message.reply_text(f"Generated Key for {days} days:\n{key}")

def ban(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("Only admin can ban users.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Use /ban <user_id>")
        return
    try:
        ban_id = int(context.args[0])
    except:
        update.message.reply_text("Please provide valid user ID.")
        return
    ban_user(ban_id)
    update.message.reply_text(f"User {ban_id} banned successfully.")

def unban(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("Only admin can unban users.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Use /unban <user_id>")
        return
    try:
        unban_id = int(context.args[0])
    except:
        update.message.reply_text("Please provide valid user ID.")
        return
    unban_user(unban_id)
    update.message.reply_text(f"User {unban_id} unbanned successfully.")

def broadcast(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("Only admin can send broadcast messages.")
        return

    message = ' '.join(context.args)
    if not message:
        update.message.reply_text("Usage: /broadcast <message>")
        return

    count = 0
    user_list = get_all_users()
    for uid in user_list:
        try:
            context.bot.send_message(uid, message)
            count += 1
        except Exception as e:
            logger.warning(f"Failed to send broadcast to {uid}: {e}")

    update.message.reply_text(f"Broadcast message sent to {count} users.")
