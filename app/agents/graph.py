import json
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# ============================================================
# STATE DEFINITION
# ============================================================
class AgentState(TypedDict):
    input: str
    intent: str
    conversation_history: List[dict]
    tools_output: str
    response: str
    patient_id: str
    thoughts: List[str]
    actions_taken: List[str]
    observations: List[str]
    confidence: float
    requires_human: bool
    iteration_count: int

# ============================================================
# TOOLS FOR CLAUDE TO CALL
# ============================================================
AVAILABLE_TOOLS = [
    {
        "name": "route_to_appointment_agent",
        "description": "Route to appointment agent for: booking, scheduling, cancelling, rescheduling appointments, checking doctor availability, urgent requests, AND any request to connect with or see a doctor/specialist/medical team (e.g. 'general medicine team', 'connect with a cardiologist', 'I want to see a doctor'). Medical specialties like general medicine, cardiology, orthopedics etc. are appointment topics, NOT pharmacy topics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why routing to this agent"
                }
            },
            "required": ["reason"]
        }
    },
    {
        "name": "ask_clarification",
        "description": "Ask user for more information when query is unclear or missing critical details",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "What to ask the user"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate to human support when confidence is low, query is too complex, or patient seems distressed or in emergency",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why escalating to human"
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "emergency"],
                    "description": "Urgency level"
                }
            },
            "required": ["reason", "urgency"]
        }
    }
]

# ============================================================
# REACT ORCHESTRATOR
# ============================================================
def react_orchestrator(state: AgentState) -> AgentState:
    """
    Core ReAct loop:
    THINK → ACT → OBSERVE → REPEAT
    """

    user_input = state["input"]
    thoughts = state.get("thoughts", [])
    actions_taken = state.get("actions_taken", [])
    observations = state.get("observations", [])
    iteration = state.get("iteration_count", 0)
    conversation = state["conversation_history"]

    # Mid-conversation fast path: if last assistant message was appointment-related,
    # route all follow-ups to appointment agent regardless of message length.
    # Prevents mid-flow clarification questions from leaking to general agent.
    if conversation:
        last_assistant = next(
            (m["content"] for m in reversed(conversation) if m["role"] == "assistant"),
            ""
        )
        appointment_signals = [
            "available", "appointment", "doctor", "dr.", "slot", "9am", "10am",
            "11am", "2pm", "3pm", "4pm", "book", "schedule", "date", "time",
            "email", "name", "reschedule", "cancel", "confirmed", "cardiolog",
            "orthoped", "neurolog", "pediatr", "dermatol", "psychiatr", "gynecol"
        ]
        if any(sig in last_assistant.lower() for sig in appointment_signals):
            state["intent"] = "appointment"
            state["confidence"] = 0.95
            return state

    # Prevent infinite loops
    if iteration >= 3:
        state["response"] = (
            "I'm having trouble processing your request. "
            "Let me connect you with our support team."
        )
        state["requires_human"] = True
        state["intent"] = "escalate"
        return state

    # Build context from previous turns
    history_summary = ""
    if conversation:
        last_messages = conversation[-4:] if len(conversation) > 4 else conversation
        history_summary = "\n".join([
            f"{m['role'].upper()}: {m['content'][:100]}..."
            if len(m['content']) > 100 else f"{m['role'].upper()}: {m['content']}"
            for m in last_messages
        ])

    # ReAct system prompt
    react_prompt = f"""You are an intelligent hospital AI orchestrator for City General Hospital.

Your job:
1. THINK about what the patient needs
2. DECIDE which tool/agent to use
3. Be confident and helpful

Patient message: "{user_input}"

Recent conversation:
{history_summary if history_summary else "No previous conversation"}

Previous thoughts: {json.dumps(thoughts) if thoughts else "None"}
Previous actions: {json.dumps(actions_taken) if actions_taken else "None"}

Think step by step:
- What does the patient need?
- Which agent handles this best?
- Do I have enough information?
- Should I escalate?

IMPORTANT: If the patient's message is a short reply, a number, a name, an email address, a date, a time, or any response that only makes sense in context (e.g. "one", "two", "yes", "no", "cancel", "9am", "John Smith", "john@gmail.com") — look at the recent conversation. If the previous AI message was about appointments, booking, doctors, scheduling, or listed appointments — route to the appointment agent. Any input that looks like an email address or a name is almost certainly a follow-up to an appointment conversation. Never route these to general.

Then call the most appropriate tool."""

    try:
        # Use full conversation so short replies like "Yes." are routed correctly
        orchestrator_messages = conversation if conversation else [{"role": "user", "content": user_input}]
        # Ensure last message is the current user input
        if not orchestrator_messages or orchestrator_messages[-1].get("content") != user_input:
            orchestrator_messages = orchestrator_messages + [{"role": "user", "content": user_input}]

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=react_prompt,
            tools=AVAILABLE_TOOLS,
            messages=orchestrator_messages
        )

        # Extract thinking
        thinking = ""
        for block in response.content:
            if hasattr(block, "text") and block.text:
                thinking = block.text
                break

        if thinking:
            thoughts.append(f"Iteration {iteration + 1}: {thinking[:200]}")

        # Extract tool call
        tool_use = None
        for block in response.content:
            if block.type == "tool_use":
                tool_use = block
                break

        # Execute tool decision
        if tool_use:
            tool_name = tool_use.name
            tool_input = tool_use.input

            actions_taken.append(f"{tool_name}: {json.dumps(tool_input)[:100]}")

            if tool_name == "route_to_appointment_agent":
                observations.append(f"Routing to appointment: {tool_input.get('reason', '')[:100]}")
                state["intent"] = "appointment"
                state["confidence"] = 0.95

            elif tool_name == "ask_clarification":
                question = tool_input.get("question", "How can I help you?")
                observations.append(f"Asking clarification: {question[:100]}")
                state["intent"] = "clarification"
                state["response"] = question
                state["confidence"] = 0.5

            elif tool_name == "escalate_to_human":
                reason = tool_input.get("reason", "")
                urgency = tool_input.get("urgency", "medium")
                observations.append(f"Escalating: {reason[:100]}")
                state["intent"] = "escalate"
                state["requires_human"] = True
                state["confidence"] = 1.0

                state["response"] = (
                    f"Connecting you with our support team. "
                    f"Priority: {urgency.upper()}. "
                    f"Our team will be with you shortly. "
                    f"For emergencies, please call 911."
                )
        else:
            # No tool called - handle as general
            state["intent"] = "general"
            state["confidence"] = 0.6

            for block in response.content:
                if hasattr(block, "text") and block.text:
                    state["response"] = block.text
                    break

    except Exception as e:
        print(f"ReAct error: {e}")
        state["intent"] = "general"
        state["confidence"] = 0.5

    # Update state
    state["thoughts"] = thoughts
    state["actions_taken"] = actions_taken
    state["observations"] = observations
    state["iteration_count"] = iteration + 1

    return state

# ============================================================
# ROUTING DECISION
# ============================================================
def decide_next(state: AgentState) -> str:
    """Route to correct agent"""

    intent = state.get("intent", "general")

    routing = {
        "appointment": "appointment",
        "clarification": "end",
        "escalate": "end",
        "general": "general"
    }

    return routing.get(intent, "general")

# ============================================================
# GENERAL AGENT (Fallback)
# ============================================================
def general_agent(state: AgentState) -> AgentState:
    """Handle general queries"""

    conversation = state["conversation_history"]
    user_input = state["input"]

    conversation.append({"role": "user", "content": user_input})

    # Detect appointment/pharmacy/reports queries that slipped through routing
    appointment_keywords = ["appointment", "availability", "book", "schedule", "cancel", "reschedule", "doctor", "slot", "dr ", "specialist", "general medicine", "cardiology", "orthopedic", "neurology", "pediatric", "dermatology", "psychiatry", "gynecology", "connect with", "see a doctor", "meet a doctor", "which doctor", "available doctor", "list doctor"]

    user_lower = user_input.lower()

    closing_keywords = ["thank you", "thanks", "thank u", "ty", "bye", "goodbye", "that's all", "thats all", "that will be all", "no that's all", "no thats all", "i'm good", "im good", "all good"]
    manage_keywords = ["cancel", "reschedule", "check my appointment", "my appointment", "upcoming appointment", "lookup", "look up"]
    new_booking_keywords = ["appointment", "availability", "book", "schedule", "doctor", "slot", "dr ", "specialist", "general medicine", "cardiology", "orthopedic", "neurology", "pediatric", "dermatology", "psychiatry", "gynecology", "connect with", "see a doctor", "meet a doctor", "which doctor", "available doctor", "list doctor"]

    if any(kw in user_lower for kw in closing_keywords):
        response_text = "Of course, take care and have a wonderful day. We are always here if you need us."

    elif any(kw in user_lower for kw in manage_keywords):
        response_text = (
            "Of course, I am happy to help with that. Could you share your email address so I can look up your appointments?"
        )

    elif any(kw in user_lower for kw in new_booking_keywords):
        response_text = (
            "I would love to help you with that. "
            "Which doctor or specialty are you looking for?"
        )
    else:
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                system="""You are a warm, calm, and caring front desk assistant at City General Hospital. Your voice is gentle and reassuring — like a real person who genuinely wants to make the patient's day a little easier.
Only answer general questions: visiting hours, location, contact number, hospital services overview.
If the question is about booking, scheduling, doctors, appointments, or anything medical — say: "I would love to help you with that. Which doctor or specialty are you looking for?"
Never attempt to answer clinical or booking questions yourself.
Tone: speak warmly and naturally. Use simple, friendly language. Never sound robotic or rushed.
Max 25 words. No emojis. No markdown. No asterisks, no bold, no bullet points. Plain text only.""",
                messages=conversation
            )
            response_text = response.content[0].text
        except Exception as e:
            response_text = "I'm having trouble processing your request right now. Please try again."
            print(f"General agent error: {e}")

    state["response"] = response_text

    conversation.append({"role": "assistant", "content": response_text})
    state["conversation_history"] = conversation

    return state

# ============================================================
# BUILD GRAPH
# ============================================================
def build_graph():
    """Build fully agentic LangGraph workflow"""

    workflow = StateGraph(AgentState)

    # Import agents
    from app.agents.appointment import appointment_agent

    # Add nodes
    workflow.add_node("react_orchestrator", react_orchestrator)
    workflow.add_node("appointment", appointment_agent)
    workflow.add_node("general", general_agent)

    # Entry point
    workflow.set_entry_point("react_orchestrator")

    # ReAct → Route directly
    workflow.add_conditional_edges(
        "react_orchestrator",
        decide_next,
        {
            "appointment": "appointment",
            "general": "general",
            "end": END
        }
    )

    # All agents → END
    workflow.add_edge("appointment", END)
    workflow.add_edge("general", END)

    return workflow.compile()

# ============================================================
# RUN AGENT
# ============================================================

# Compile once at startup
try:
    graph = build_graph()
    print("✅ LangGraph compiled successfully")
except Exception as e:
    print(f"❌ LangGraph error: {e}")
    graph = None

def run_agent(
    user_input: str,
    conversation_history: list,
    patient_id: str = "patient_1"
) -> tuple:
    """Run the fully agentic graph"""

    if not graph:
        return "System error. Please try again.", conversation_history

    initial_state = {
        "input": user_input,
        "intent": "",
        "conversation_history": conversation_history,
        "tools_output": "",
        "response": "",
        "patient_id": patient_id,
        "thoughts": [],
        "actions_taken": [],
        "observations": [],
        "confidence": 0.0,
        "requires_human": False,
        "iteration_count": 0
    }

    try:
        final_state = graph.invoke(initial_state)
        return final_state["response"], final_state["conversation_history"]
    except Exception as e:
        print(f"Graph error: {e}")
        return f"Error processing request: {str(e)}", conversation_history