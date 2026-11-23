import httpx
import logging
import os

logger = logging.getLogger(__name__)

TTS_VOICE = os.getenv("TTS_VOICE", "alloy")  # Options: alloy, nova, shimmer, echo, fable, onyx
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def text_to_audio_bytes(text: str) -> bytes:
    if not text or len(text.strip()) < 3:
        logger.warning("TTS received empty or too-short text. Skipping.")
        return b""

    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    try:
        logger.info(f"TTS converting ({len(text)} chars) with voice '{TTS_VOICE}'")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tts-1",
                    "input": text,
                    "voice": TTS_VOICE,
                    "response_format": "mp3"
                }
            )

        if response.status_code != 200:
            raise RuntimeError(f"OpenAI TTS error: {response.status_code} {response.text}")

        audio_bytes = response.content
        logger.info(f"TTS complete: {len(audio_bytes) / 1024:.1f} KB")
        return audio_bytes

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise