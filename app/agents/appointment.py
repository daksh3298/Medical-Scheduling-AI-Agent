import json
import os
from datetime import date as today_date
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

DOCTOR_EMAIL = os.getenv("DOCTOR_EMAIL")

# ============================================================
# DATA HELPERS
# ============================================================
def load_doctors():
    with open("app/data/doctors.json", "r") as f:
        return json.load(f)

def get_doctor_by_name(name: str) -> dict:
    for doctor in load_doctors()["doctors"]:
        if name.lower() in doctor["name"].lower():
            return doctor
    return None

def get_doctors_by_specialty(specialty: str) -> list:
    return [
        d for d in load_doctors()["doctors"]
        if specialty.lower() in d["specialty"].lower()
    ]

def check_availability(doctor: dict, date: str) -> dict:
    try:
        from app.services.google_meet import get_doctor_calendar_availability
        result = get_doctor_calendar_availability(DOCTOR_EMAIL, date)
        return {
            "doctor_name": doctor["name"],
            "doctor_specialty": doctor["specialty"],
            "date": date,
            "available_slots": result.get("available_slots", []),
        }
    except Exception as e:
        print(f"Calendar error: {e}")
        return {
            "doctor_name": doctor["name"],
            "doctor_specialty": doctor["specialty"],
            "date": date,
            "available_slots": ["9am", "10am", "11am", "2pm", "3pm", "4pm"],
        }

# ============================================================
# TOOLS
# ============================================================
APPOINTMENT_TOOLS = [
    {
        "name": "list_doctors",
        "description": "List all available doctors at the hospital with their specialties.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "check_doctor_availability",
        "description": "Check available appointment slots for a doctor (by name or specialty) on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doctor_name": {"type": "string", "description": "Doctor name or specialty"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format. Convert any natural language date (tomorrow, next Thursday, this Friday, etc.) to YYYY-MM-DD yourself using today's date from the system prompt — never ask the user to reformat."}
            },
            "required": ["doctor_name", "date"]
        }
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment. Requires doctor name, date, time, patient full name (must be explicitly given by patient — never guessed from email), and patient email.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doctor_name":   {"type": "string"},
                "date":          {"type": "string", "description": "YYYY-MM-DD. Convert natural language dates (tomorrow, next Monday, etc.) to YYYY-MM-DD using today's date — never ask the user to reformat."},
                "time":          {"type": "string", "description": "e.g. 9am, 2pm"},
                "patient_name":  {"type": "string", "description": "Full name of the patient"},
                "patient_email": {"type": "string", "description": "Patient email for confirmation"}
            },
            "required": ["doctor_name", "date", "time", "patient_name", "patient_email"]
        }
    },
    {
        "name": "send_confirmation_email",
        "description": "Resend a confirmation email for a booked appointment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email":   {"type": "string"},
                "summary": {"type": "string", "description": "Appointment summary to include"}
            },
            "required": ["email", "summary"]
        }
    },
    {
        "name": "lookup_appointments",
        "description": "Look up upcoming appointments for a patient by their email address. Use this before rescheduling or cancelling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_email": {"type": "string", "description": "Patient's email address"}
            },
            "required": ["patient_email"]
        }
    },
    {
        "name": "reschedule_appointment",
        "description": "Reschedule an existing appointment to a new date and time using the event ID from lookup_appointments. Will check if the new slot is available first — if not, returns available slots so you can offer alternatives to the patient.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id":      {"type": "string", "description": "Google Calendar event ID from lookup_appointments"},
                "new_date":      {"type": "string", "description": "New date in YYYY-MM-DD format. Convert natural language dates using today's date."},
                "new_time":      {"type": "string", "description": "New time e.g. 9am, 2pm"},
                "patient_email": {"type": "string", "description": "Patient email to send reschedule confirmation"},
                "patient_name":  {"type": "string", "description": "Patient name for the confirmation email"}
            },
            "required": ["event_id", "new_date", "new_time", "patient_email"]
        }
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel an existing appointment using the event ID from lookup_appointments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id":      {"type": "string", "description": "Google Calendar event ID"},
                "patient_email": {"type": "string", "description": "Patient email to send cancellation confirmation"}
            },
            "required": ["event_id", "patient_email"]
        }
    }
]

# ============================================================
# TOOL EXECUTION
# ============================================================
def execute_tool(name: str, inputs: dict) -> str:
    if name == "list_doctors":
        doctors = load_doctors()["doctors"]
        return "Available doctors: " + ", ".join(
            f"{d['name']} ({d['specialty']})" for d in doctors
        )

    elif name == "check_doctor_availability":
        doctor_name = inputs["doctor_name"]
        date = inputs["date"]

        doctor = get_doctor_by_name(doctor_name)
        if not doctor:
            matches = get_doctors_by_specialty(doctor_name)
            if matches:
                lines = []
                for d in matches:
                    slots = check_availability(d, date).get("available_slots", [])
                    lines.append(f"{d['name']}: {', '.join(slots) if slots else 'no slots'}")
                return "\n".join(lines)
            return f"No doctor found matching '{doctor_name}'."

        slots = check_availability(doctor, date).get("available_slots", [])
        if slots:
            return f"{doctor['name']} ({doctor['specialty']}) is available on {date} at: {', '.join(slots)}."
        return f"{doctor['name']} has no availability on {date}."

    elif name == "book_appointment":
        doctor    = get_doctor_by_name(inputs["doctor_name"])
        if not doctor:
            return f"Doctor '{inputs['doctor_name']}' not found."

        date  = inputs["date"]
        time  = inputs["time"]
        slots = check_availability(doctor, date).get("available_slots", [])
        if not (time in slots or any(time.lower() in s.lower() for s in slots)):
            return f"{time} is not available. Slots: {', '.join(slots)}."

        try:
            from app.services.google_meet import create_meet_appointment
            booking = create_meet_appointment(
                doctor_name=doctor["name"],
                doctor_email=DOCTOR_EMAIL,
                patient_name=inputs["patient_name"],
                patient_email=inputs["patient_email"],
                date=date,
                time=time,
                specialty=doctor["specialty"]
            )
            if booking["status"] == "success":
                return (
                    f"Booked. Doctor: {doctor['name']}, Date: {date}, Time: {time}. "
                    f"Meet link: {booking['meet_link']}. "
                    f"Confirmation sent to {inputs['patient_email']}."
                )
            return f"Booking failed: {booking['message']}"
        except Exception as e:
            return f"Error: {str(e)}"

    elif name == "send_confirmation_email":
        try:
            from app.services.google_meet import _send_email
            body = (
                f"Appointment Confirmation - City General Hospital\n\n"
                f"{inputs['summary']}\n\n"
                f"For queries, contact us at (619) 555-0100."
            )
            _send_email(
                inputs["email"],
                "Appointment Confirmation - City General Hospital",
                body
            )
            return f"Confirmation email sent to {inputs['email']}."
        except Exception as e:
            return f"Failed to send email: {str(e)}"

    elif name == "lookup_appointments":
        try:
            from app.services.google_meet import lookup_appointments
            result = lookup_appointments(inputs["patient_email"])
            appts = result.get("appointments", [])
            if not appts:
                return f"No upcoming appointments found for {inputs['patient_email']}."
            lines = []
            for a in appts:
                lines.append(
                    f"- {a['summary']} on {a['date']} at {a['time']} (ID: {a['event_id']})"
                )
            return "Upcoming appointments:\n" + "\n".join(lines)
        except Exception as e:
            return f"Lookup failed: {str(e)}"

    elif name == "reschedule_appointment":
        try:
            from app.services.google_meet import reschedule_appointment, _send_email
            # Check availability before rescheduling
            new_date = inputs["new_date"]
            new_time = inputs["new_time"]
            try:
                from app.services.google_meet import get_doctor_calendar_availability
                avail = get_doctor_calendar_availability(DOCTOR_EMAIL, new_date)
                slots = avail.get("available_slots", [])
                if slots and not (new_time in slots or any(new_time.lower() in s.lower() for s in slots)):
                    return f"{new_time} is not available on {new_date}. Available slots: {', '.join(slots)}."
            except Exception:
                pass  # If availability check fails, proceed with reschedule
            result = reschedule_appointment(
                inputs["event_id"], new_date, new_time
            )
            if result["status"] == "success":
                patient_email = inputs.get("patient_email", "")
                patient_name  = inputs.get("patient_name", "Patient")
                if patient_email:
                    body = (
                        f"Appointment Rescheduled - City General Hospital\n\n"
                        f"Patient : {patient_name}\n"
                        f"New Date: {inputs['new_date']}\n"
                        f"New Time: {inputs['new_time']}\n"
                        f"Location: City General Hospital\n\n"
                        f"For queries, contact us at (619) 555-0100."
                    )
                    _send_email(
                        patient_email,
                        f"Appointment Rescheduled - City General Hospital",
                        body
                    )
                return f"Rescheduled to {inputs['new_date']} at {inputs['new_time']}. Confirmation sent to {patient_email}."
            return f"Reschedule failed: {result['message']}"
        except Exception as e:
            return f"Reschedule error: {str(e)}"

    elif name == "cancel_appointment":
        try:
            from app.services.google_meet import cancel_appointment, _send_email
            result = cancel_appointment(inputs["event_id"])
            if result["status"] == "success":
                _send_email(
                    inputs["patient_email"],
                    "Appointment Cancelled - City General Hospital",
                    f"Your appointment has been cancelled.\n\nFor queries, contact us at (619) 555-0100."
                )
                return f"Appointment cancelled. Confirmation sent to {inputs['patient_email']}."
            return f"Cancellation failed: {result['message']}"
        except Exception as e:
            return f"Cancel error: {str(e)}"

    return "Unknown tool."

# ============================================================
# APPOINTMENT AGENT
# ============================================================
def appointment_agent(state: dict) -> dict:
    conversation = state["conversation_history"]
    user_input   = state["input"]

    conversation.append({"role": "user", "content": user_input})

    system_prompt = f"""You are a warm, calm, and caring front desk assistant at City General Hospital. Your voice is gentle and reassuring — like a real person who genuinely wants to make the patient's day a little easier.
Today: {today_date.today().strftime('%Y-%m-%d')} ({today_date.today().strftime('%B %d, %Y')})

Use your tools to help patients book, check, reschedule, or cancel appointments.

Tone: speak warmly and naturally. Use simple, friendly language. Never sound robotic or rushed. Be patient and encouraging.

HARD RULE — NO EXCEPTIONS: You must NEVER call any tool without first confirming the input back to the patient and receiving their explicit confirmation (yes, correct, yep, that's right, etc.). This rule cannot be skipped under any circumstance, even if the input seems obvious or was just provided.

After the patient provides ANY of the following, your ONLY allowed response is to repeat it back and ask if it is correct. You are NOT allowed to call any tool until the patient says yes:
- Email address: read it back character by character spelling each letter, saying "at" for @, "dot" for ., and "underscore" for _. Example: "I have your email as j-o-h-n at g-m-a-i-l dot c-o-m — is that correct?"
- Full name: "Your name is John Smith — correct?"
- Date: "That is Monday May 18th — correct?"
- Time: "9am — correct?"
- Doctor or specialty: "Dr. Jay, General Physician — correct?"

EXAMPLE — lookup flow:
Patient: "my email is john@gmail.com"
You: "I have your email as j-o-h-n at g-m-a-i-l dot c-o-m — is that correct?"
Patient: "yes"
You: [NOW call lookup_appointments]

If the patient has not said yes or correct, do NOT call any tool. Always confirm first.

When the patient mentions any date in natural language (tomorrow, next Thursday, this Friday, in 3 days, etc.) — convert it to YYYY-MM-DD yourself. Never ask the patient to rephrase a date.
For reschedule or cancel: call lookup_appointments with their email first to get the event ID, then call reschedule_appointment or cancel_appointment. Always pass patient_email (and patient_name if known) to reschedule_appointment so a confirmation email can be sent.
Never answer questions about existing appointments from memory or conversation context. Any question about who the doctor is, what time an appointment is, or what is booked — always call lookup_appointments with the patient's email first. If you do not have their email, ask for it.
Before calling book_appointment, you MUST have the patient's full name AND email — both must be explicitly stated by the patient. Never infer or guess the name from the email address. If either is missing, ask before proceeding.
When a patient speaks their email, it arrives as words: "john dot smith at gmail dot com" — convert it to proper format: john.smith@gmail.com. Apply this conversion silently before confirming it back to the patient.
Max 25 words per response. Ask one question at a time. No emojis. No markdown. No asterisks, no bold, no bullet points. Plain text only."""

    # Use conversation history as messages, with current user input as last entry
    messages = list(conversation)

    response_text = "I couldn't process your request. Please try again."

    for _ in range(5):  # allow up to 5 tool calls per turn
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=system_prompt,
            tools=APPOINTMENT_TOOLS,
            messages=messages
        )

        tool_block  = next((b for b in response.content if b.type == "tool_use"), None)
        text_block  = next((b for b in response.content if hasattr(b, "text")), None)

        if response.stop_reason == "tool_use" and tool_block:
            tool_result = execute_tool(tool_block.name, tool_block.input)
            print(f"Tool: {tool_block.name} → {tool_result[:80]}")

            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": tool_result
                }]
            })
        else:
            response_text = text_block.text if text_block else response_text
            break

    state["response"] = response_text
    state["tools_output"] = ""

    # Save full messages (including tool calls/results) so event IDs persist across turns
    messages.append({"role": "assistant", "content": response_text})
    state["conversation_history"] = messages

    return state
