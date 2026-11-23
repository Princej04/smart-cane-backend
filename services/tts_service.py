import edge_tts
import logging
from config import TTS_VOICE

logger = logging.getLogger(__name__)


async def text_to_audio_bytes(text: str) -> bytes:
    # Safety guard — don't attempt TTS on empty or garbage input
    if not text or len(text.strip()) < 3:
        logger.warning("TTS received empty or too-short text. Skipping.")
        return b""

    try:
        logger.info(f"TTS converting ({len(text)} chars) with voice '{TTS_VOICE}'")

        communicate = edge_tts.Communicate(text=text, voice=TTS_VOICE)

        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        audio_bytes = b"".join(audio_chunks)
        logger.info(f"TTS complete: {len(audio_bytes) / 1024:.1f} KB")
        return audio_bytes

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise