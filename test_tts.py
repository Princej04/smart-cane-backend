# save as test_tts.py in your backend folder
import asyncio
import edge_tts

async def test():
    text = "You are facing an open doorway on your left."
    communicate = edge_tts.Communicate(text=text, voice="en-US-AriaNeural")
    with open("tts_test.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
    import os
    size = os.path.getsize("tts_test.mp3")
    print(f"Done. File size: {size} bytes")

asyncio.run(test())