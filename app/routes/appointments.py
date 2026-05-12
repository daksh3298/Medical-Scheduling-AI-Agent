import json
import os
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# ============================================================
# REQUEST MODELS
# ============================================================
class BookRequest(BaseModel):
    patient_name: str
    patient_email: str
    doctor_name: str
    date: str
    time: str

class CancelRequest(BaseModel):
    event_id: str

class RescheduleRequest(BaseModel):
    event_id: str
    new_date: str
    new_time: str

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def load_doctors():
    with open("app/data/doctors.json", "r") as f:
        return json.load(f)

def get_doctor_by_name(name: str):
    doctors = load_doctors()
    for doctor in doctors["doctors"]:
        if name.lower() in doctor["name"].lower():
            return doctor
    return None

def get_doctors_by_specialty(specialty: str):
    doctors = load_doctors()
    return [
        d for d in doctors["doctors"]
        if specialty.lower() in d["specialty"].lower()
    ]

# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/api/doctors")
def get_all_doctors():
    """Get all doctors"""
    doctors = load_doctors()
    return {"doctors": doctors["doctors"]}

@router.get("/api/doctors/specialty/{specialty}")
def get_doctors_by_spec(specialty: str):
    """Get doctors by specialty"""
    doctors = get_doctors_by_specialty(specialty)
    return {"doctors": doctors}

@router.get("/api/doctors/{doctor_name}/availability")
def get_availability(doctor_name: str, date: str):
    """Get doctor availability for a specific date"""

    doctor = get_doctor_by_name(doctor_name)

    if not doctor:
        return {"error": f"Doctor {doctor_name} not found"}

    try:
        from app.services.google_meet import get_doctor_calendar_availability
        availability = get_doctor_calendar_availability(
            os.getenv("DOCTOR_EMAIL"),
            date
        )
        return {
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "date": date,
            "available_slots": availability.get("available_slots", [])
        }
    except Exception as e:
        return {
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "date": date,
            "available_slots": ["9am", "10am", "11am", "2pm", "3pm", "4pm"],
            "note": "Showing default slots"
        }

@router.post("/api/appointments/book")
def book_appointment_endpoint(request: BookRequest):
    """Book appointment directly via API"""

    try:
        from app.services.google_meet import create_meet_appointment

        result = create_meet_appointment(
            doctor_name=request.doctor_name,
            doctor_email=os.getenv("DOCTOR_EMAIL"),
            patient_name=request.patient_name,
            patient_email=request.patient_email,
            date=request.date,
            time=request.time,
            specialty="General Medicine"
        )
        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/appointments/cancel")
def cancel_appointment_endpoint(request: CancelRequest):
    """Cancel appointment"""

    try:
        from app.services.google_meet import cancel_appointment
        result = cancel_appointment(request.event_id)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/appointments/reschedule")
def reschedule_appointment_endpoint(request: RescheduleRequest):
    """Reschedule appointment"""

    try:
        from app.services.google_meet import reschedule_appointment
        result = reschedule_appointment(
            request.event_id,
            request.new_date,
            request.new_time
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}