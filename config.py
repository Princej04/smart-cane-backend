import os
from dotenv import load_dotenv

load_dotenv()

# --- AI Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- TTS Configuration ---
# Edge-TTS voice. Good options for an assistive app:
# "en-US-AriaNeural"  → natural, conversational
# "en-US-GuyNeural"   → clear male voice
# "en-IN-NeerjaNeural" → Indian English female
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-AriaNeural")

# --- Image Processing ---
# Image is resized on the Pi before sending, but we re-validate here
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB hard limit

# --- System Prompt for Gemini ---
# This is the single most important tuning knob for response quality.
# Keep responses short and spoken-word friendly (no bullet points, no markdown).
SYSTEM_PROMPT = """You are a concise assistant embedded in a smart cane for a visually impaired user.
The user will ask a question about what is in front of them. You will receive an image.

Strict rules:
- Always respond in exactly 1 to 2 complete sentences. Never leave a sentence unfinished.
- Maximum 40 words total. Count your words before responding.
- No bullet points, no lists, no markdown.
- Lead with the most important information — hazards first.
- Speak naturally as if describing to someone standing next to you.
- If the image is unclear, say so in one sentence.
"""
