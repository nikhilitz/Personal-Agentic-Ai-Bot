# /Users/nikhilgupta/Desktop/Mem0nic/controller.py
import os
import asyncio
import json
from datetime import datetime
from state import MemeBotState
from nodes.instagram_login import instagram_login
from nodes.download_reel import download_reel
from nodes.generate_caption_with_llm import generate_caption_with_llm
from nodes.post_reel import post_reel
from nodes.generate_mail import generate_mail_with_llm
from nodes.send_mail import send_mail
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from cryptography.fernet import Fernet

# Load env
from dotenv import load_dotenv
load_dotenv()

# Load encryption key for logging
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher_suite = Fernet(ENCRYPTION_KEY)

async def process_reel(url, theme, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Controller callback: runs the full Instagram posting workflow up to the approval step.
    """
    state = MemeBotState()
    state.reel_url = url
    state.reel_theme = theme
    state.IG_USERNAME = os.getenv("IG_USERNAME")
    state.IG_PASSWORD = os.getenv("IG_PASSWORD")
    state.IG_2FA_SECRET = os.getenv("IG_2FA_SECRET")
    
    try:
        # Step 1: Download Reel
        state = download_reel(state)
        if not state.reel_file_path:
            raise Exception("Reel download failed.")
        
        # Step 2: Generate Caption
        state = generate_caption_with_llm(state)
        
        # Store pending data for user
        context.user_data["pending_reel"] = {
            "url": url,
            "theme": theme,
            "caption": state.caption,
            "file_path": state.reel_file_path
        }
        
        # Ask for confirmation
        keyboard = [
            [InlineKeyboardButton("Post Now", callback_data="confirm_post")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_post")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message_text = (
            f"✅ **Reel Preview Ready!**\n\n"
            f"**URL:** {url}\n"
            f"**Theme:** {theme}\n\n"
            f"**Generated Caption:**\n{state.caption}\n\n"
            f"Looks good? Choose an option:"
        )

        await update.message.reply_text(message_text, reply_markup=reply_markup)
        
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to process reel: {e}")

async def confirm_post_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the final approval and posts the reel, then deletes the file.
    """
    query = update.callback_query
    pending = context.user_data.get("pending_reel")
    
    if not pending:
        await query.edit_message_text("❌ No pending reel found.")
        return

    state = MemeBotState()
    state.reel_file_path = pending["file_path"]
    state.caption = pending["caption"]
    state.IG_USERNAME = os.getenv("IG_USERNAME")
    state.IG_PASSWORD = os.getenv("IG_PASSWORD")
    state.IG_2FA_SECRET = os.getenv("IG_2FA_SECRET")
    
    try:
        instagram_login(state)
        state = post_reel(state)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": query.from_user.id,
            "action": "post_reel",
            "url": pending["url"],
            "theme": pending["theme"],
            "caption": state.caption,
            "status": "success"
        }
        json_log = json.dumps(log_entry).encode('utf-8')
        encrypted_log = cipher_suite.encrypt(json_log)

        with open("post_log.encrypted", "ab") as f:
            f.write(encrypted_log + b'\n')
            
        await query.edit_message_text(f"✅ Reel posted successfully!\nCaption:\n{state.caption}")
        
    except Exception as e:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": query.from_user.id,
            "action": "post_reel",
            "url": pending["url"],
            "theme": pending["theme"],
            "status": "failed",
            "error": str(e)
        }
        json_log = json.dumps(log_entry).encode('utf-8')
        encrypted_log = cipher_suite.encrypt(json_log)

        with open("post_log.encrypted", "ab") as f:
            f.write(encrypted_log + b'\n')
            
        await query.edit_message_text(f"⚠️ Failed to post reel: {e}")
        
    finally:
        if pending and "file_path" in pending:
            try:
                os.remove(pending["file_path"])
                thumbnail_path = pending["file_path"].replace(".mp4", ".jpg")
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            except OSError as e:
                print(f"Error deleting files: {e}")
        
        context.user_data.pop("pending_reel", None)

async def cancel_post_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the cancellation of a reel post and deletes the files.
    """
    query = update.callback_query
    pending = context.user_data.get("pending_reel")
    
    if pending and "file_path" in pending:
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": query.from_user.id,
                "action": "cancel_post",
                "url": pending["url"],
                "status": "success",
                "message": "User cancelled post, files deleted."
            }
            json_log = json.dumps(log_entry).encode('utf-8')
            encrypted_log = cipher_suite.encrypt(json_log)

            with open("post_log.encrypted", "ab") as f:
                f.write(encrypted_log + b'\n')
                
            os.remove(pending["file_path"])
            thumbnail_path = pending["file_path"].replace(".mp4", ".jpg")
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            
        except OSError as e:
            print(f"Error deleting files: {e}")
            
    context.user_data.pop("pending_reel", None)
    await query.message.reply_text("❌ Post cancelled. Files deleted.")


async def process_email(company_email, company_description, designation, update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = MemeBotState()
    state.company_email_id = company_email
    state.company_description = company_description
    state.designation = designation
    state.SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    state.SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    try:
        state = generate_mail_with_llm(state)
        
        context.user_data['pending_email'] = {
            "subject": state.mail_subject,
            "body": state.mail_body,
            "to": state.company_email_id
        }

        keyboard = [
            [InlineKeyboardButton("Approve and Send", callback_data="send_mail_confirm")],
            [InlineKeyboardButton("Cancel", callback_data="send_mail_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"⏳ Generated Mail Preview:\n\n"
            f"To: {state.company_email_id}\n"
            f"Subject: {state.mail_subject}\n\n"
            f"Body:\n{state.mail_body}\n\n"
            f"Do you approve sending this email?",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to generate email: {e}")
        
async def confirm_send_mail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    pending_email = context.user_data.get('pending_email')
    if not pending_email:
        await query.edit_message_text("❌ No pending email found.")
        return
        
    state = MemeBotState()
    state.company_email_id = pending_email['to']
    state.mail_subject = pending_email['subject']
    state.mail_body = pending_email['body']
    state.SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    state.SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    
    await query.edit_message_text("⏳ Sending email...")
    
    try:
        state = send_mail(state)
        if state.email_sent:
            await query.edit_message_text("✅ Email sent successfully!")
        else:
            await query.edit_message_text("⚠️ Failed to send email.")
            
    except Exception as e:
        await query.edit_message_text(f"⚠️ Failed to send email: {e}")
        
    finally:
        context.user_data.pop('pending_email', None)

if __name__ == "__main__":
    from nodes.bot_node import TelegramBotNode
    # Wrap the run() call in a loop with an error handler
    while True:
        try:
            bot_node = TelegramBotNode(
                reel_controller_callback=process_reel,
                email_controller_callback=process_email
            )
            bot_node.run()
        except Exception as e:
            print(f"⚠️ Bot crashed with an error: {e}. Restarting...")
            asyncio.sleep(5) # Wait for 5 seconds before restarting
