import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
from create_workspace_user import create_user, set_token_content, user_exists, delete_user, delete_all_users
from pathlib import Path
from telegram.constants import ChatAction

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

LIVE_DOMAIN_PATH = Path("domain.txt")
TOKEN_PATH = Path("token.json")

# States for create user flow
(USERNAME, GIVEN_NAME, FAMILY_NAME, RECOVERY_EMAIL, RECOVERY_PHONE, ORG_UNIT) = range(6)
ADD_TOKEN = 100  # Custom state for token conversation

user_sessions = {}

# Remove the cancel handler function
def get_live_domain():
    return LIVE_DOMAIN_PATH.read_text().strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = get_live_domain()
    is_admin = update.effective_chat.id == ADMIN_CHAT_ID
    admin_cmds = "\n\n*Admin Commands:*\n/setdomain <domain>\n/addnewtoken" if is_admin else ""
    await update.message.reply_text(
        f"👋 Welcome to *Bulk GoogleGen Bot!*\n\n"
        f"🌐 *Live domain*: `{domain}`\n\n"
        f"Use /createuser to create a new user." + admin_cmds,
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions.pop(update.effective_chat.id, None)
    context.user_data.clear()
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END  # <--- this is crucial!

async def createuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter desired username (e.g., `john`):")
    return USERNAME

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    username = update.message.text.strip()
    domain = get_live_domain()
    email = f"{username}@{domain}"
    exists = user_exists(email)
    if exists:
        await update.message.reply_text("❌ Username already exists. Please enter a different username:")
        return USERNAME
    context.user_data['username'] = username
    await update.message.reply_text("Enter *given name* (e.g., John):", parse_mode='Markdown')
    return GIVEN_NAME

async def handle_given_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.user_data['given_name'] = update.message.text.strip()
    await update.message.reply_text("Enter *family name* (e.g., Doe):", parse_mode='Markdown')
    return FAMILY_NAME

async def handle_family_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.user_data['family_name'] = update.message.text.strip()
    await update.message.reply_text("Enter recovery email (optional, type 'skip' to leave blank):")
    return RECOVERY_EMAIL

async def handle_recovery_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    text = update.message.text.strip()
    context.user_data['recovery_email'] = None if text.lower() == 'skip' else text
    await update.message.reply_text("Enter recovery phone (optional, type 'skip' to leave blank):")
    return RECOVERY_PHONE

async def handle_recovery_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    text = update.message.text.strip()
    context.user_data['recovery_phone'] = None if text.lower() == 'skip' else text
    await update.message.reply_text("Enter orgUnit path (default is '/', type 'skip' to use default):")
    return ORG_UNIT

async def handle_org_unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    org_unit = update.message.text.strip()
    if org_unit.lower() == 'skip' or not org_unit:
        org_unit = "/"
    data = context.user_data
    username = data['username']
    domain = get_live_domain()
    email = f"{username}@{domain}"
    user = {
        "primaryEmail": email,
        "givenName": data['given_name'],
        "familyName": data['family_name'],
        "recoveryEmail": data.get("recovery_email"),
        "recoveryPhone": data.get("recovery_phone"),
        "orgUnitPath": org_unit
    }
    pwd = create_user(user)
    if pwd:
        await update.message.reply_text(
            f"✅ User created:\n👤 *{email}*\n🔑 *{pwd}*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to create user. Try again.")
    return ConversationHandler.END

async def setdomain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return await update.message.reply_text("⛔ Not authorized.")
    parts = update.message.text.split()
    if len(parts) != 2:
        return await update.message.reply_text("Usage: /setdomain new.domain.com")
    new_domain = parts[1].strip()
    LIVE_DOMAIN_PATH.write_text(new_domain)
    await update.message.reply_text(f"✅ Domain updated to `{new_domain}`", parse_mode='Markdown')

async def addnewtoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return await update.message.reply_text("⛔ Not authorized.")
    await update.message.reply_text("Please send the *content* of the new token.json file:", parse_mode='Markdown')
    return ADD_TOKEN

async def save_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    try:
        content = update.message.text
        set_token_content(content)
        await update.message.reply_text("✅ token.json updated.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    return ConversationHandler.END

async def delete_single_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return await update.message.reply_text("⛔ Not authorized.")
    parts = update.message.text.split()
    if len(parts) != 2:
        return await update.message.reply_text("Usage: /delete <email>")
    email = parts[1].strip()
    if delete_user(email):
        await update.message.reply_text(f"✅ User {email} deleted.")
    else:
        await update.message.reply_text(f"❌ Failed to delete user {email}.")

async def delete_all_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return await update.message.reply_text("⛔ Not authorized.")
    domain = get_live_domain()
    await update.message.reply_text("⚠️ Deleting all users in domain. This may take a while...")
    if delete_all_users(domain):
        await update.message.reply_text("✅ All users deleted.")
    else:
        await update.message.reply_text("❌ Failed to delete all users.")

def main():
    print("[INFO] Telegram bot is running. Press Ctrl+C to stop.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    # Remove the cancel handler and all /cancel command references
    app.add_handler(CommandHandler("setdomain", setdomain))

    # Handler for creating user
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("createuser", createuser)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username)],
            GIVEN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_given_name)],
            FAMILY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_family_name)],
            RECOVERY_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recovery_email)],
            RECOVERY_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recovery_phone)],
            ORG_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_org_unit)],
        },
        fallbacks=[]
    ))

    # Handler for updating token
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addnewtoken", addnewtoken)],
        states={ADD_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_token)]},
        fallbacks=[]
    ))

    app.add_handler(CommandHandler("delete", delete_single_user))
    app.add_handler(CommandHandler("deleteall", delete_all_users_cmd))

    app.run_polling()

if __name__ == "__main__":
    main()
