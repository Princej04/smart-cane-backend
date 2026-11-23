import asyncio
from google import genai
from google.genai import types
from PIL import Image
import io
import logging
from config import GEMINI_API_KEY, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is not set in your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


async def get_ai_response(question: str, image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    logger.info(f"Sending to Gemini | Question: '{question}' | Image size: {image.size}")

    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image, question],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    max_output_tokens=500,
                )
            )
            answer = response.text.strip()
            logger.info(f"Gemini response (attempt {attempt + 1}): '{answer}'")
            return answer

        except Exception as e:
            last_error = e
            wait = 2 ** attempt  # 1s → 2s → 4s
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
            await asyncio.sleep(wait)

    logger.error(f"Gemini API error after 3 attempts: {last_error}")
    raise last_error