"""
test_client.py — Simulates the Raspberry Pi sending a request to the backend.

Usage:
    python test_client.py
    python test_client.py --image path/to/img.jpg
    python test_client.py --question "Is there a door in front of me?"
"""

import httpx
import asyncio
import argparse
import os
import sys

BACKEND_URL = "http://localhost:8000"
OUTPUT_AUDIO_FILE = "test_response.mp3"


def create_test_image() -> bytes:
    try:
        from PIL import Image, ImageDraw
        import io

        img = Image.new("RGB", (640, 480), color=(135, 180, 120))
        draw = ImageDraw.Draw(img)
        draw.rectangle([200, 150, 440, 330], fill=(180, 100, 60))
        draw.rectangle([270, 230, 370, 330], fill=(80, 50, 30))
        draw.text((250, 100), "Test Scene", fill=(255, 255, 255))

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return buffer.getvalue()

    except ImportError:
        print("Pillow not installed. Run: pip install Pillow")
        sys.exit(1)


async def test_health():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            data = response.json()
            print(f"✅ Health check: {data['message']}")
            return True
        except httpx.ConnectError:
            print(f"❌ Cannot connect to backend at {BACKEND_URL}")
            print("   Make sure the server is running: uvicorn main:app")
            return False


async def test_ask(question: str, image_path: str | None = None):
    import time

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        print(f"📷 Using image: {image_path} ({len(image_bytes)/1024:.1f} KB)")
    else:
        print("📷 No image provided — generating test image.")
        image_bytes = create_test_image()
        print(f"   Generated test image: {len(image_bytes)/1024:.1f} KB")

    print(f"❓ Question: '{question}'")
    print(f"🚀 Sending request to {BACKEND_URL}/ask ...")

    start = time.time()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/ask",
            data={"question": question},
            files={"image": ("capture.jpg", image_bytes, "image/jpeg")}
        )

    elapsed = time.time() - start

    if response.status_code != 200:
        print(f"❌ Server returned {response.status_code}: {response.text}")
        return

    ai_text = response.headers.get("X-AI-Response-Text", "")
    if ai_text:
        print(f"\n🤖 AI Response Text: \"{ai_text}\"")

    audio_bytes = response.content
    with open(OUTPUT_AUDIO_FILE, "wb") as f:
        f.write(audio_bytes)

    print(f"✅ Success!")
    print(f"   Audio size: {len(audio_bytes) / 1024:.1f} KB")
    print(f"   Total round-trip time: {elapsed:.2f}s")
    print(f"\n🔊 Audio saved to: {OUTPUT_AUDIO_FILE}")
    print(f"   Open it in any media player to verify.")


async def main():
    parser = argparse.ArgumentParser(description="Test client for Smart Cane backend.")
    parser.add_argument(
        "--question", "-q",
        default="What do you see in front of me? Are there any obstacles?",
        help="The question to ask the AI."
    )
    parser.add_argument(
        "--image", "-i",
        default=None,
        help="Path to a JPEG image file."
    )
    args = parser.parse_args()

    print("=" * 55)
    print("  Smart Cane Backend — Test Client")
    print("=" * 55)

    if not await test_health():
        return

    print()
    await test_ask(question=args.question, image_path=args.image)


if __name__ == "__main__":
    asyncio.run(main())