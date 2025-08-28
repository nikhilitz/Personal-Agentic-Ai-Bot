# /Users/nikhilgupta/Desktop/Mem0nic/nodes/download_reel.py
import os
import subprocess
import yt_dlp
from urllib.parse import urlparse
from datetime import datetime

def download_reel(state):
    """
    Download Instagram reel in best video + audio quality into 'reels' folder.
    Filenames are unique using Reel ID + timestamp.
    """
    if not state.reel_url:
        print("⚠️ No reel URL provided.")
        return state

    os.makedirs("reels", exist_ok=True)

    # Extract reel ID
    path_parts = urlparse(state.reel_url).path.split('/')
    reel_id = next((part for part in path_parts if part), "reel")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"reels/{reel_id}_{timestamp}.mp4"

    # yt-dlp options for best video + audio
    ydl_opts = {
        "outtmpl": output_file,
        "quiet": True,
        "noplaylist": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],
        "merge_output_format": "mp4",
        "overwrites": True
    }
    
    # Check if a combined format is available, if not, download separately
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(state.reel_url, download=False)
            formats = info.get('formats', None)
            
            # Check for a single format with both video and audio
            has_combined_format = any(f.get('vcodec') != 'none' and f.get('acodec') != 'none' for f in formats)
            
            if has_combined_format:
                ydl.download([state.reel_url])
                state.reel_file_path = output_file
                print(f"✅ Reel downloaded in best quality: {output_file}")
            else:
                # Fallback to separate download and merge if needed
                print("Falling back to separate video and audio download and merge...")
                video_file = f"reels/{reel_id}_{timestamp}_video.mp4"
                audio_file = f"reels/{reel_id}_{timestamp}_audio.m4a"
                
                ydl_opts_video = {
                    "outtmpl": video_file,
                    "quiet": True,
                    "noplaylist": True,
                    "format": "bestvideo[ext=mp4]"
                }
                ydl_opts_audio = {
                    "outtmpl": audio_file,
                    "quiet": True,
                    "noplaylist": True,
                    "format": "bestaudio[ext=m4a]"
                }
                
                with yt_dlp.YoutubeDL(ydl_opts_video) as ydl_vid:
                    ydl_vid.download([state.reel_url])
                
                with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl_aud:
                    ydl_aud.download([state.reel_url])
                
                # Merge using ffmpeg silently
                if os.path.exists(video_file) and os.path.exists(audio_file):
                    subprocess.run([
                        "ffmpeg", "-y", "-loglevel", "error",
                        "-i", video_file,
                        "-i", audio_file,
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-b:a", "192k",
                        output_file
                    ], check=True)
        
                    state.reel_file_path = output_file
                    print(f"✅ Reel downloaded and merged: {output_file}")
        
                    # Cleanup
                    os.remove(video_file)
                    os.remove(audio_file)
                else:
                    raise Exception("Video or audio missing after download")
                
    except Exception as e:
        print(f"⚠️ Reel download failed: {e}")

    return state
