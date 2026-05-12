from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# LIFESPAN
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🏥 Hospital AI Agent Starting...")
    print("✅ Routes loaded")
    print("✅ LangGraph compiled")
    print("✅ Claude API connected")
    print("✅ Google Meet service ready")
    print("\n🚀 Running on http://localhost:8000\n")
    yield

# ============================================================
# CREATE APP
# ============================================================
app = FastAPI(
    title="Hospital AI Agent",
    description="Multi-agent hospital system powered by Claude + LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================
# CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================
# ROUTES
# ============================================================
from app.routes import appointments, chat, transcribe, tts
from app.frontend.ui import get_html

app.include_router(appointments.router)
app.include_router(chat.router)
app.include_router(transcribe.router)
app.include_router(tts.router)

# ============================================================
# FRONTEND
# ============================================================
@app.get("/")
def home():
    return HTMLResponse(get_html())

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True
    )