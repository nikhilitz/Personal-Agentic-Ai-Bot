# /Users/nikhilgupta/Desktop/Mem0nic/nodes/send_mail.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_mail(state):
    """
    Sends an email using SMTP with the generated subject and body.
    """
    if not hasattr(state, "company_email_id") or not state.company_email_id:
        raise ValueError("MemeBotState.company_email_id must be set.")
    if not hasattr(state, "mail_subject") or not state.mail_subject:
        raise ValueError("MemeBotState.mail_subject must be set.")
    if not hasattr(state, "mail_body") or not state.mail_body:
        raise ValueError("MemeBotState.mail_body must be set.")

    # Get credentials from environment variables
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    
    if not sender_email or not sender_password:
        raise ValueError("SENDER_EMAIL and SENDER_PASSWORD must be set in .env")
    
    try:
        # Create a multipart message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = state.mail_subject
        msg["From"] = sender_email
        msg["To"] = state.company_email_id
        
        # Attach the email body
        msg.attach(MIMEText(state.mail_body, "plain"))
        
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, state.company_email_id, msg.as_string())
        
        state.email_sent = True
        print(f"✅ Email successfully sent to {state.company_email_id}")
        
    except Exception as e:
        print(f"⚠️ Failed to send email: {e}")
        state.email_sent = False
        
    return state