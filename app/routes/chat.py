from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.graph import run_agent

router = APIRouter()

# Store conversation histories per session
conversation_store = {}

# ============================================================
# REQUEST MODELS
# ============================================================
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    patient_id: str = "patient_1"

# ============================================================
# CHAT ENDPOINT
# ============================================================
@router.post("/api/chat")
def chat(request: ChatRequest):
    """
    Main chat endpoint
    Receives user message → runs through LangGraph → returns response
    """

    session_id = request.session_id
    patient_id = request.patient_id
    user_message = request.message

    # Get or create conversation history
    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation_history = conversation_store[session_id]

    try:
        # Run through LangGraph
        response, updated_history = run_agent(
            user_input=user_message,
            conversation_history=conversation_history,
            patient_id=patient_id
        )

        # Update conversation store
        conversation_store[session_id] = updated_history

        return {
            "response": response,
            "session_id": session_id,
            "status": "success"
        }

    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "response": "I encountered an error. Please try again.",
            "session_id": session_id,
            "status": "error",
            "error": str(e)
        }

# ============================================================
# CLEAR CONVERSATION
# ============================================================
@router.post("/api/chat/clear")
def clear_conversation(session_id: str = "default"):
    """Clear conversation history for a session"""

    if session_id in conversation_store:
        conversation_store[session_id] = []

    return {
        "status": "cleared",
        "session_id": session_id
    }

# ============================================================
# HEALTH CHECK
# ============================================================
@router.get("/api/health")
def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "message": "Hospital AI Agent is running"
    }