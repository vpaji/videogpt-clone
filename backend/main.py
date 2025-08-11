from fastapi import FastAPI, UploadFile, Form
import requests, os, uuid, subprocess

app = FastAPI()

GEMINI_API_KEY = os.getenv("AIzaSyBafGD7obI2F7rV8XsNKG2dHUuoUho6K2Y")

@app.post("/generate")
async def generate_video(topic: str = Form(...), style: str = Form(...)):
    # Step 1: Get script from Gemini
    gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Write a short video script about {topic} in {style} style"}]}]
    }
    r = requests.post(f"{gemini_url}?key={AIzaSyBafGD7obI2F7rV8XsNKG2dHUuoUho6K2Y}", headers=headers, json=payload)
    script_text = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    # Step 2: Generate image using Pollinations.ai
    image_url = f"https://image.pollinations.ai/prompt/{topic.replace(' ', '%20')}%20{style}"
    img_data = requests.get(image_url).content
    img_path = f"temp_{uuid.uuid4()}.jpg"
    with open(img_path, "wb") as f:
        f.write(img_data)

    # Step 3: TTS using Coqui API
    tts_url = "https://tts.api.cloud.your-coqui-instance"  # Replace with your TTS endpoint
    audio_path = f"temp_{uuid.uuid4()}.mp3"
    # This is a placeholder for actual TTS call
    with open(audio_path, "wb") as f:
        f.write(b"")  # Empty for now

    # Step 4: Assemble video with ffmpeg
    video_path = f"video_{uuid.uuid4()}.mp4"
    subprocess.run([
        "ffmpeg", "-loop", "1", "-i", img_path, "-i", audio_path,
        "-c:v", "libx264", "-t", "5", "-pix_fmt", "yuv420p", video_path
    ])

    return {"script": script_text, "video_url": video_path}
