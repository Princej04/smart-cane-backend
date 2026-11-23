import logging
import io

logger = logging.getLogger(__name__)


async def text_to_audio_bytes(text: str) -> bytes:
    if not text or len(text.strip()) < 3:
        logger.warning("TTS received empty or too-short text. Skipping.")
        return b""

    try:
        from gtts import gTTS
        import asyncio

        logger.info(f"TTS converting ({len(text)} chars) with gTTS")

        # gTTS is synchronous — run in executor to avoid blocking async loop
        loop = asyncio.get_event_loop()

        def generate():
            tts = gTTS(text=text, lang="en", slow=False)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            return buffer.getvalue()

        audio_bytes = await loop.run_in_executor(None, generate)
        logger.info(f"TTS complete: {len(audio_bytes) / 1024:.1f} KB")
        return audio_bytes

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise