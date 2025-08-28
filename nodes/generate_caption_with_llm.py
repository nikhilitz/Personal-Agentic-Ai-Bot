# /Users/nikhilgupta/Desktop/Mem0nic/nodes/generate_caption_with_llm.py
import os
import re
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI  

# Load env
load_dotenv()

def clean_caption(raw_text):
    """
    Clean the raw text from LLM:
    - Remove **bold markers**
    - Remove extra whitespace
    - Strip leading/trailing spaces
    """
    if not isinstance(raw_text, str):
        raise TypeError(f"Expected string, got {type(raw_text)}")
    text = re.sub(r'\*\*', '', raw_text)  
    text = text.strip()
    return text

def generate_caption_with_llm(state):
    """
    Generates Instagram caption in Hinglish, Mem0nic guidelines,
    and hashtags using LLM. Always includes #mem0nic.
    Stores the final cleaned text in state.caption.
    """
    if not hasattr(state, "reel_theme") or not state.reel_theme:
        raise ValueError("MemeBotState.reel_theme must be set before calling this node.")

    theme = state.reel_theme

    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")

    llm = ChatOpenAI(
        model_name="provider-6/gpt-5-nano",
        temperature=0.7,
        openai_api_key=api_key,
        openai_api_base=api_base,
    )

    # The prompt with your exact specifications
    chat_prompt = f"""
Generate Instagram reel content for the theme: "{theme}" in HINGLISH
(casual, catchy, relatable). 

Format:
- Start with a catchy caption in Hinglish.
- Then add Mem0nic Official Guidelines:
✨ Mem0nic Official Guidelines ✨  
⚠️ This content is just for entertainment purposes only.  
🎥 Credit goes to the original creator of the video/content.  
📩 DM for credits/removal.  
❤️ Stay tuned for more fun and laughter!  

- Then generate hashtags:
  - At least 10 viral/trending hashtags which always works on all reels
  - 10 relatable hashtags
  - 5 hashtags for adjustment/trends
- ALWAYS include #mem0nic in hashtags
- Do NOT include markdown like **Caption** or **Hashtags**
- Output as a single plain text block
"""

    response = llm.invoke(chat_prompt)
    raw_text = response.text()

    state.caption = clean_caption(raw_text)

    print("✅ Caption + guidelines + hashtags generated:")
    print(state.caption)

    return state