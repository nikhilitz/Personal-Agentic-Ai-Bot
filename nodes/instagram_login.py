import os
import pyotp
import json
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from state import MemeBotState
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables at the top of the file
load_dotenv()

# Your encryption key must be loaded from .env here
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
cipher_suite = Fernet(ENCRYPTION_KEY)

def instagram_login(state: MemeBotState):
    """
    Logs into Instagram with session management.
    Saves session to a file for reuse. Handles login_required errors.
    """
    print("🔹 Logging in to Instagram...")

    session_file = "ig_session.encrypted"
    state.session_file = session_file
    client = Client()

    # Try loading existing encrypted session
    try:
        if os.path.exists(session_file):
            with open(session_file, "rb") as f:
                encrypted_data = f.read()
                decrypted_data = cipher_suite.decrypt(encrypted_data)
                
                # Fix: Assign the decrypted dictionary directly to the client's settings
                client.settings = json.loads(decrypted_data.decode('utf-8'))
                
                print("✅ Loaded existing Instagram session")
        
        # Check if the loaded session is still valid
        # This will trigger a LoginRequired exception if not
        if client.get_timeline_feed() is not None:
            print("✅ Session is valid.")
            state.client = client
            return state

    except LoginRequired:
        print("⚠️ Session expired or invalid. Attempting new login...")
        
    except Exception as e:
        print(f"⚠️ Failed to load or verify session: {e}. Attempting new login...")

    # Fallback to a full login with username, password, and 2FA
    if not state.IG_USERNAME or not state.IG_PASSWORD or not state.IG_2FA_SECRET:
        raise ValueError("Instagram credentials and 2FA secret must be set to re-login")

    try:
        # Generate a new OTP
        totp = pyotp.TOTP(state.IG_2FA_SECRET)
        code = totp.now()

        # Attempt to log in with a new session
        client.login(state.IG_USERNAME, state.IG_PASSWORD, verification_code=code)
        
        # Save the new encrypted session
        encrypted_settings = cipher_suite.encrypt(json.dumps(client.settings).encode('utf-8'))
        with open(session_file, "wb") as f:
            f.write(encrypted_settings)
        
        print("✅ Logged in and saved new encrypted session successfully!")
        state.client = client
        
    except Exception as e:
        raise Exception(f"Failed to log in to Instagram: {e}")

    return state