import os
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    voice: str = "aura-asteria-en"

@router.post("/api/tts")
async def text_to_speech(req: TTSRequest):
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="DEEPGRAM_API_KEY not set")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                "https://api.deepgram.com/v1/speak",
                headers={
                    "Authorization": f"Token {api_key}",
                    "Content-Type": "application/json"
                },
                params={"model": req.voice},
                json={"text": req.text[:4096]}
            )

        if res.status_code != 200:
            print(f"Deepgram TTS error {res.status_code}: {res.text}")
            raise HTTPException(status_code=502, detail=f"Deepgram TTS error: {res.text}")

        audio_bytes = res.content
        if not audio_bytes:
            raise HTTPException(status_code=502, detail="Empty audio from Deepgram TTS")

        print(f"TTS OK — {len(audio_bytes)} bytes for {len(req.text)} chars")
        return Response(content=audio_bytes, media_type="audio/mpeg")

    except HTTPException:
        raise
    except Exception as e:
        print(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
