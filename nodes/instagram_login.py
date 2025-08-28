# /Users/nikhilgupta/Desktop/Mem0nic/nodes/instagram_login.py
import os
import pyotp
from instagrapi import Client
from state import MemeBotState

def instagram_login(state: MemeBotState):
    """
    Logs into Instagram with session management.
    Saves session to a file for reuse.
    """
    print("🔹 Logging in to Instagram...")

    session_file = "ig_session.json"
    state.session_file = session_file
    client = Client()

    # Try loading existing session
    if os.path.exists(session_file):
        client.load_settings(session_file)
        print("✅ Loaded existing Instagram session")
    else:
        if not state.IG_USERNAME or not state.IG_PASSWORD or not state.IG_2FA_SECRET:
            raise ValueError("Instagram credentials and 2FA secret must be set")

        # Generate OTP
        totp = pyotp.TOTP(state.IG_2FA_SECRET)
        code = totp.now()

        client.login(state.IG_USERNAME, state.IG_PASSWORD, verification_code=code)
        client.dump_settings(session_file)
        print("✅ Logged in and saved session successfully!")

    state.client = client