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
        
    # Check if the client is already logged in
    if not hasattr(state, "client") or not state.client:
        raise Exception("Instagram client not found in state. Login failed.")

    try:
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

        # Use the client object passed through the state
        state.client.video_upload(path=media_path, caption=caption_text, thumbnail=thumbnail_path)
        print("✅ Reel posted successfully!")

    except Exception as e:
        print(f"⚠️ Reel upload failed: {e}")
        # The `login_required` message is handled by instagram_login.py now

    return state