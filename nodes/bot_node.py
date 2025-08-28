import os
import asyncio
from datetime import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from controller import confirm_post_reel, cancel_post_reel, process_reel, process_email, confirm_send_mail

# Load env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
PASSWORD = os.getenv("POSTER_PASSWORD")  
EMAIL_KEY_PHRASE = os.getenv("EMAIL_KEY_PHRASE")
APPROVED_USERS_FILE = ".approved_users"

# Load approved users from file
if os.path.exists(APPROVED_USERS_FILE):
    with open(APPROVED_USERS_FILE, "r") as f:
        APPROVED_USERS = set(int(u.strip()) for u in f.readlines())
else:
    APPROVED_USERS = set()

class TelegramBotNode:
    def __init__(self, reel_controller_callback, email_controller_callback):
        self.reel_controller_callback = reel_controller_callback
        self.email_controller_callback = email_controller_callback
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.user_pending_password = {}
        self.user_pending_action = {}
        self.user_pending_key_phrase = {}
        
        # FIX: Added a timeout to prevent re-processing of updates
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).read_timeout(60).connect_timeout(60).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hey! Send 'hey poster' to check approval status."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        text = update.message.text.strip()

        # --- Admin stop ---
        if user_id == ADMIN_USER_ID and text.lower() == "stop":
            await update.message.reply_text("⚠️ Server stopping by admin command!")
            print("Server stopped by admin command")
            os._exit(0)

        # --- Approval flow ---
        if text.lower() == "hey poster":
            if user_id in APPROVED_USERS:
                keyboard = [
                    [InlineKeyboardButton("Post a Reel 🎥", callback_data="start_reel_flow")],
                    [InlineKeyboardButton("Send a Mail 📧", callback_data="start_email_flow")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "You are approved to use Mem0nic! ✅\nWhat would you like to do?",
                    reply_markup=reply_markup
                )
            else:
                self.user_pending_password[user_id] = True
                await update.message.reply_text(
                    "You are not approved yet. Please send the password to get approval."
                )
            return

        # --- Handle password for new user ---
        if self.user_pending_password.get(user_id):
            if text == PASSWORD:
                APPROVED_USERS.add(user_id)
                self.user_pending_password.pop(user_id)
                with open(APPROVED_USERS_FILE, "a") as f:
                    f.write(f"{user_id}\n")
                await update.message.reply_text(
                    "✅ Approved! Now you can choose an action."
                )
            else:
                await update.message.reply_text("❌ Incorrect password. Try again.")
            return

        # --- Handle key phrase for email flow ---
        if self.user_pending_key_phrase.get(user_id):
            if text == EMAIL_KEY_PHRASE:
                self.user_pending_key_phrase.pop(user_id)
                context.user_data['action'] = 'email'
                await update.message.reply_text("✅ Key phrase accepted. Now send me the email details in the format: `Company Email | Company Description | Designation`")
            else:
                await update.message.reply_text("❌ Incorrect key phrase. Try again.")
            return

        # --- Approved user starting reel workflow
        if user_id in APPROVED_USERS and "|" in text and context.user_data.get('action') == 'reel':
            url, theme = map(str.strip, text.split("|", 1))
            await update.message.reply_text("⏳ Downloading reel and generating caption...")
            asyncio.create_task(
                self.reel_controller_callback(url, theme, update, context)
            )
            context.user_data.pop('action')
            return
        
        # --- Approved user sending email info ---
        if user_id in APPROVED_USERS and "|" in text and context.user_data.get('action') == 'email':
            try:
                company_email, company_description, designation = map(str.strip, text.split("|", 2))
                await update.message.reply_text("⏳ Generating email content...")
                asyncio.create_task(
                    self.email_controller_callback(company_email, company_description, designation, update, context)
                )
            except ValueError:
                await update.message.reply_text("❌ Invalid format! Use 'Company Email | Company Description | Designation'")
            context.user_data.pop('action')
            return

        # --- General unhandled message
        await update.message.reply_text("❌ I don't understand that command. Please start with 'hey poster'.")


    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()

        # --- Start flows ---
        if query.data == "start_reel_flow":
            context.user_data['action'] = 'reel'
            await query.message.reply_text("Okay, let's post a reel! Send me the content in the format: `URL | theme`")
            return
        
        if query.data == "start_email_flow":
            self.user_pending_key_phrase[user_id] = True
            await query.edit_message_text("Please provide the email key phrase to proceed.")
            return

        # --- Handle reel approval buttons
        if query.data == "confirm_post":
            await query.edit_message_text("⏳ Posting in progress...")
            await confirm_post_reel(update, context)
            return

        if query.data == "cancel_post":
            await query.edit_message_text("❌ Post cancelled. Files deleted.")
            await cancel_post_reel(update, context)
            return
        
        # --- Handle email confirmation buttons ---
        if query.data == "send_mail_confirm":
            await confirm_send_mail(update, context)
            return

        if query.data == "send_mail_cancel":
            context.user_data.pop('pending_email', None)
            await query.edit_message_text("❌ Email sending cancelled.")
            return
        
        # --- Scheduling logic from here on ---
        pending = context.user_data.get("pending_reel")
        if not pending:
            await query.edit_message_text("❌ No pending reel found.")
            return
            
        if query.data == "schedule":
            days = ["Today", "Tomorrow", "Day After"]
            keyboard = [[InlineKeyboardButton(day, callback_data=f"day_{i}")] for i, day in enumerate(days)]
            context.user_data["schedule_step"] = {"pending": pending}
            await query.edit_message_text("Select day to schedule:", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        if query.data.startswith("day_"):
            step = context.user_data.get("schedule_step")
            if not step: return
            day_index = int(query.data.split("_")[1])
            target_day = datetime.now() + timedelta(days=day_index)
            step["target_day"] = target_day

            keyboard = []
            for h in range(24):
                for m in [0, 30]:
                    hour_str = f"{h:02d}:{m:02d}"
                    keyboard.append([InlineKeyboardButton(hour_str, callback_data=f"hour_{hour_str}")])
            await query.edit_message_text(
                "Select hour and minute for posting:", 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        if query.data.startswith("hour_"):
            step = context.user_data.get("schedule_step")
            if not step: return
            hour_str = query.data.split("_")[1]
            target_day = step["target_day"]
            hour, minute = map(int, hour_str.split(":"))
            run_time = target_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
            pending = step["pending"]

            self.scheduler.add_job(
                lambda: asyncio.run(self.reel_controller_callback(pending["url"], pending["theme"], update, context)),
                trigger="date",
                run_date=run_time
            )
            await query.edit_message_text(f"✅ Scheduled successfully for {run_time}")
            context.user_data.pop("pending_reel", None)
            context.user_data.pop("schedule_step", None)

    def run(self):
        print("🚀 Telegram bot started...")
        self.app.run_polling()
        
if __name__ == "__main__":
    from controller import process_reel, process_email
    bot_node = TelegramBotNode(
        reel_controller_callback=process_reel,
        email_controller_callback=process_email
    )
    bot_node.run()