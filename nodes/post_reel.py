# /Users/nikhilgupta/Desktop/Mem0nic/nodes/post_reel.py
import os
import subprocess
from instagrapi import Client

def post_reel(state):
    """
    Upload the downloaded reel to Instagram in high quality with the caption.
    """
    if not hasattr(state, "reel_file_path") or not state.reel_file_path:
        print("⚠️ No reel file found to post.")
        return state

    if not hasattr(state, "caption") or not state.caption:
        print("⚠️ No caption available to post.")
        return state

    try:
        cl = Client()
        session_file = "ig_session.json"

        # Load or login
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            print("✅ Loaded existing Instagram session.")
        else:
            cl.login(username=state.IG_USERNAME, password=state.IG_PASSWORD)
            cl.dump_settings(session_file)
            print("✅ Logged in and saved new session.")

        media_path = state.reel_file_path
        caption_text = state.caption.strip()

        # Ensure #mem0nic exists
        if "#mem0nic" not in caption_text.lower():
            caption_text += " #mem0nic"

        # Generate thumbnail if missing
        thumbnail_path = media_path.replace(".mp4", ".jpg")
        if not os.path.exists(thumbnail_path):
            subprocess.run([
                "ffmpeg", "-y", "-i", media_path,
                "-ss", "00:00:01.000", "-frames:v", "1", "-update", "1",
                thumbnail_path
            ], check=True)

        # Upload in high quality (instagrapi auto handles IG compression)
        cl.video_upload(path=media_path, caption=caption_text, thumbnail=thumbnail_path)
        print("✅ Reel posted successfully!")

    except Exception as e:
        print(f"⚠️ Reel upload failed: {e}")

    return state