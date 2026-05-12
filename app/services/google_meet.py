import os
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

TIME_MAP = {
    "9am": "09:00", "9:00am": "09:00",
    "10am": "10:00", "10:00am": "10:00",
    "11am": "11:00", "11:00am": "11:00",
    "12pm": "12:00", "12:00pm": "12:00",
    "1pm": "13:00", "1:00pm": "13:00",
    "2pm": "14:00", "2:00pm": "14:00",
    "3pm": "15:00", "3:00pm": "15:00",
    "4pm": "16:00", "4:00pm": "16:00",
    "5pm": "17:00", "5:00pm": "17:00",
}


DOCTOR_CALENDAR_ID = os.getenv("DOCTOR_EMAIL", "primary")

def _get_service():
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)


def _parse_slot(date: str, time: str):
    time_24 = TIME_MAP.get(time.lower().replace(" ", ""), "09:00")
    start = datetime.strptime(f"{date} {time_24}", "%Y-%m-%d %H:%M")
    end = start + timedelta(minutes=30)
    return start, end


def _jitsi_link(event_id: str) -> str:
    room = f"CityGeneralHospital-{event_id[:12]}"
    return f"https://meet.jit.si/{room}"


def _make_ics(uid: str, start: datetime, end: datetime,
              summary: str, description: str, location: str,
              organizer_email: str, attendee_emails: list) -> bytes:
    """Generate an iCalendar (.ics) file content."""
    fmt = "%Y%m%dT%H%M%S"
    attendee_lines = "\n".join(
        f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN={e}:mailto:{e}"
        for e in attendee_emails
    )
    ics = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//City General Hospital//EN\n"
        "METHOD:REQUEST\n"
        "BEGIN:VEVENT\n"
        f"UID:{uid}\n"
        f"DTSTAMP:{datetime.utcnow().strftime(fmt)}Z\n"
        f"DTSTART:{start.strftime(fmt)}\n"
        f"DTEND:{end.strftime(fmt)}\n"
        f"SUMMARY:{summary}\n"
        f"DESCRIPTION:{description.replace(chr(10), '\\n')}\n"
        f"LOCATION:{location}\n"
        f"ORGANIZER;CN=City General Hospital:mailto:{organizer_email}\n"
        f"{attendee_lines}\n"
        "BEGIN:VALARM\n"
        "TRIGGER:-PT30M\n"
        "ACTION:DISPLAY\n"
        "DESCRIPTION:Appointment reminder\n"
        "END:VALARM\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )
    return ics.encode("utf-8")


def _send_email(to: str, subject: str, body: str, ics_bytes: bytes = None):
    sender = os.getenv("GMAIL_SENDER", "")
    password = os.getenv("GMAIL_APP_PASSWORD", "")
    if not sender or not password:
        print("Email not sent: GMAIL_SENDER or GMAIL_APP_PASSWORD not configured.")
        return

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.attach(MIMEText(body, "plain"))

    if ics_bytes:
        part = MIMEBase("text", "calendar", method="REQUEST", name="appointment.ics")
        part.set_payload(ics_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="appointment.ics")
        part.add_header("Content-Type", 'text/calendar; method=REQUEST; charset="UTF-8"')
        msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to, msg.as_string())
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Email error to {to}: {e}")


# ============================================================
# CHECK AVAILABILITY
# ============================================================
def get_doctor_calendar_availability(doctor_email: str, date: str) -> dict:
    try:
        service = _get_service()
        all_slots = ["9am", "10am", "11am", "2pm", "3pm", "4pm"]

        day_start = datetime.strptime(date, "%Y-%m-%d").replace(hour=0, minute=0)
        day_end = day_start + timedelta(days=1)

        body = {
            "timeMin": day_start.isoformat() + "Z",
            "timeMax": day_end.isoformat() + "Z",
            "items": [{"id": "primary"}],
        }
        freebusy = service.freebusy().query(body=body).execute()
        busy_periods = freebusy.get("calendars", {}).get("primary", {}).get("busy", [])

        busy_hours = set()
        for period in busy_periods:
            s = datetime.fromisoformat(period["start"].replace("Z", ""))
            busy_hours.add(s.hour)

        available = [
            slot for slot in all_slots
            if int(TIME_MAP[slot].split(":")[0]) not in busy_hours
        ]
        return {"available_slots": available}

    except Exception as e:
        print(f"Availability check error: {e}")
        return {"available_slots": ["9am", "10am", "11am", "2pm", "3pm", "4pm"]}


# ============================================================
# BOOK APPOINTMENT
# ============================================================
def create_meet_appointment(
    doctor_name: str,
    doctor_email: str,
    patient_name: str,
    patient_email: str,
    date: str,
    time: str,
    specialty: str,
) -> dict:
    try:
        service = _get_service()
        start, end = _parse_slot(date, time)
        event_id = str(uuid.uuid4())[:12]
        meet_link = _jitsi_link(event_id)

        event = {
            "summary": f"Medical Appointment – {specialty}",
            "description": (
                f"Patient: {patient_name}\n"
                f"Patient Email: {patient_email}\n"
                f"Doctor: {doctor_name} ({specialty})\n"
                f"Date: {date}  |  Time: {time}\n"
                f"Hospital: City General Hospital\n"
                f"Video Call: {meet_link}\n\n"
                f"Please arrive / join 5 minutes early."
            ),
            "start": {"dateTime": start.isoformat(), "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": end.isoformat(), "timeZone": "America/Los_Angeles"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        result = service.events().insert(calendarId=DOCTOR_CALENDAR_ID, body=event).execute()
        cal_event_id = result["id"]

        # Build ICS calendar invite
        ics_uid = str(uuid.uuid4())
        sender = os.getenv("GMAIL_SENDER", doctor_email)
        ics = _make_ics(
            uid=ics_uid,
            start=start,
            end=end,
            summary=f"Medical Appointment – {specialty}",
            description=(
                f"Patient: {patient_name}\n"
                f"Doctor: {doctor_name} ({specialty})\n"
                f"Video Call: {meet_link}\n"
                f"Hospital: City General Hospital"
            ),
            location="City General Hospital",
            organizer_email=sender,
            attendee_emails=[doctor_email, patient_email],
        )

        # Send confirmation emails with .ics attachment
        email_body = f"""
Appointment Confirmed – City General Hospital

Patient : {patient_name}
Doctor  : {doctor_name} ({specialty})
Date    : {date}
Time    : {time}
Location: City General Hospital

Video Call Link: {meet_link}

Confirmation ID: {cal_event_id}

Please arrive / join 5 minutes early.
Open the attached appointment.ics file to add this event to your Google Calendar.
For cancellations contact us at (619) 555-0100.
        """.strip()

        _send_email(patient_email, f"Appointment Confirmed – {doctor_name} on {date}", email_body, ics)
        _send_email(doctor_email,  f"New Patient Appointment – {patient_name} on {date}", email_body, ics)

        return {
            "status": "success",
            "event_id": cal_event_id,
            "meet_link": meet_link,
            "message": "Appointment booked. Confirmation emails sent.",
        }

    except Exception as e:
        print(f"Booking error: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================
# LOOKUP APPOINTMENTS BY PATIENT EMAIL
# ============================================================
def lookup_appointments(patient_email: str) -> dict:
    try:
        service = _get_service()
        now = datetime.utcnow().isoformat() + "Z"
        print(f"Lookup: searching calendar '{DOCTOR_CALENDAR_ID}' for '{patient_email}' from {now}")
        result = service.events().list(
            calendarId=DOCTOR_CALENDAR_ID,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
            q=patient_email
        ).execute()

        events = result.get("items", [])
        print(f"Lookup: found {len(events)} events")
        appointments = []
        for e in events:
            start_raw = e.get("start", {}).get("dateTime", "")
            if not start_raw:
                continue
            start_dt = datetime.fromisoformat(start_raw.replace("Z", ""))
            appointments.append({
                "event_id": e["id"],
                "summary": e.get("summary", "Appointment"),
                "date": start_dt.strftime("%Y-%m-%d"),
                "time": start_dt.strftime("%I:%M %p").lstrip("0"),
                "description": e.get("description", "")
            })

        return {"appointments": appointments}
    except Exception as e:
        print(f"Lookup error: {e}")
        return {"appointments": [], "error": str(e)}


# ============================================================
# CANCEL APPOINTMENT
# ============================================================
def cancel_appointment(event_id: str) -> dict:
    try:
        service = _get_service()
        service.events().delete(calendarId=DOCTOR_CALENDAR_ID, eventId=event_id).execute()
        return {"status": "success", "message": "Appointment cancelled successfully."}
    except Exception as e:
        print(f"Cancel error: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================
# RESCHEDULE APPOINTMENT
# ============================================================
def reschedule_appointment(event_id: str, new_date: str, new_time: str) -> dict:
    try:
        service = _get_service()
        event = service.events().get(calendarId=DOCTOR_CALENDAR_ID, eventId=event_id).execute()

        start, end = _parse_slot(new_date, new_time)
        event["start"] = {"dateTime": start.isoformat(), "timeZone": "America/Los_Angeles"}
        event["end"] = {"dateTime": end.isoformat(), "timeZone": "America/Los_Angeles"}

        updated = service.events().update(
            calendarId=DOCTOR_CALENDAR_ID, eventId=event_id, body=event
        ).execute()

        return {
            "status": "success",
            "event_id": updated["id"],
            "message": f"Appointment rescheduled to {new_date} at {new_time}.",
        }
    except Exception as e:
        print(f"Reschedule error: {e}")
        return {"status": "error", "message": str(e)}
