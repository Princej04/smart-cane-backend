import logging
import time
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from PIL import Image
from services.ai_service import get_ai_response
from services.tts_service import text_to_audio_bytes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Cane Backend",
    description="Receives image + question from the cane, returns spoken audio response.",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Smart Cane backend is running."}


@app.post("/ask")
async def ask(
    question: str = Form(...),
    image: UploadFile = File(...)
):
    start_time = time.time()
    logger.info(f"--- New Request ---")
    logger.info(f"Question: '{question}'")
    logger.info(f"Image: {image.filename} | {image.content_type}")

    # --- Validate image type ---
    if image.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type '{image.content_type}'. Send JPEG or PNG."
        )

    # --- Read and compress image ---
    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Image file is empty.")

    original_size = len(image_bytes) / 1024
    logger.info(f"Image received: {original_size:.1f} KB")

    # Compress if larger than 50KB — keeps Gemini fast
    if len(image_bytes) > 50 * 1024:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img = pil_img.convert("RGB")
        pil_img.thumbnail((640, 480))
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG", quality=70)
        image_bytes = buffer.getvalue()
        logger.info(f"Image compressed: {original_size:.1f} KB → {len(image_bytes) / 1024:.1f} KB")

    # --- Get AI response ---
    try:
        ai_text = await get_ai_response(question=question, image_bytes=image_bytes)
    except Exception:
        raise HTTPException(status_code=500, detail="AI service failed. Check server logs.")

    ai_time = time.time()
    logger.info(f"Gemini done in {ai_time - start_time:.2f}s")

    # --- Convert text to audio bytes ---
    try:
        audio_bytes = await text_to_audio_bytes(ai_text)
    except Exception:
        raise HTTPException(status_code=500, detail="TTS service failed. Check server logs.")

    tts_time = time.time()
    logger.info(f"TTS done in {tts_time - ai_time:.2f}s")
    logger.info(f"Audio size: {len(audio_bytes) / 1024:.1f} KB")
    logger.info(f"Total round trip: {tts_time - start_time:.2f}s")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"X-AI-Response-Text": ai_text[:200]}
    )