# /Users/nikhilgupta/Desktop/Mem0nic/state.py
from typing import Optional, List
from instagrapi import Client

class MemeBotState:
    """
    Central state model for MemeBot workflow.
    Nodes read and update this state.
    """
    # --- Credentials ---
    IG_USERNAME: Optional[str] = None
    IG_PASSWORD: Optional[str] = None
    IG_2FA_SECRET: Optional[str] = None
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None

    # --- Instagram client ---
    client: Optional[Client] = None
    session_file: Optional[str] = None

    # --- Reel info ---
    reel_url: Optional[str] = None
    reel_file_path: Optional[str] = None
    reel_theme: Optional[str] = None

    # --- Caption info ---
    caption: Optional[str] = None

    # --- Upload info ---
    post_url: Optional[str] = None
    upload_status: Optional[bool] = None
    
    # --- Email info ---
    company_email_id: Optional[str] = None
    company_description: Optional[str] = None
    designation: Optional[str] = None
    mail_subject: Optional[str] = None
    mail_body: Optional[str] = None
    email_sent: Optional[bool] = None

    # --- Logging / History ---
    log: List[dict] = []

    def add_log(self, action: str, details: dict):
        self.log.append({"action": action, "details": details})