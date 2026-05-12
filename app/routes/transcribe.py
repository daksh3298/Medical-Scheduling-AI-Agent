import os
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/api/deepgram-key")
async def get_deepgram_key():
    key = os.getenv("DEEPGRAM_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="DEEPGRAM_API_KEY not set")
    return JSONResponse({"key": key})

@router.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="DEEPGRAM_API_KEY not set")

    audio_bytes = await audio.read()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={
                    "Authorization": f"Token {api_key}",
                    "Content-Type": "audio/webm"
                },
                params={
                    "model": "nova-2",
                    "smart_format": "true",
                    "detect_language": "true",
                    "filler_words": "false",
                    "punctuate": "true"
                },
                content=audio_bytes
            )

        if res.status_code != 200:
            print(f"Deepgram STT error {res.status_code}: {res.text}")
            raise HTTPException(status_code=502, detail=f"Deepgram STT error: {res.text}")

        data = res.json()
        transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
        confidence = data["results"]["channels"][0]["alternatives"][0].get("confidence", 0)

        print(f"STT: '{transcript}' (confidence: {confidence:.2f})")
        return {"transcript": transcript, "confidence": confidence}

    except HTTPException:
        raise
    except Exception as e:
        print(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
