# Hospital AI Voice Agent

A production-ready conversational AI agent for hospital appointment management. Patients interact via natural voice to book, reschedule, cancel, and look up appointments — eliminating manual scheduling touchpoints through a real-time voice pipeline.

---

## Overview

This system replaces traditional phone-based hospital scheduling with a voice AI agent. A patient clicks **Start Call**, speaks naturally, and the agent handles the entire scheduling workflow — availability check, identity verification, booking, and confirmation email — in a single conversation.

**Stack:** FastAPI · LangGraph · Anthropic Claude · Deepgram STT/TTS · Google Calendar · Google Meet

---

## Architecture

```
User Voice
    ↓
Deepgram STT (nova-2)          — speech to text, real-time streaming
    ↓
ReAct Orchestrator (Claude)    — intent classification + agent routing
    ↓
┌─────────────────────┬──────────────────────┐
Appointment Agent      General Agent
(book, reschedule,     (hospital info,
cancel, lookup)        visiting hours, FAQs)
    ↓
Google Calendar API    — real-time availability + booking
Google Meet API        — auto-generates Meet link per appointment
Gmail API              — sends confirmation email
    ↓
Groq TTS (Deepgram)    — text to speech response
    ↓
User hears response
```

### Multi-Agent Pipeline

| Agent | Role |
|---|---|
| **ReAct Orchestrator** | Classifies intent using Claude tool calls, routes to the correct agent |
| **Appointment Agent** | Handles all scheduling workflows with 7 tools |
| **General Agent** | Handles FAQs, greetings, hospital info |

### Appointment Agent Tools

| Tool | Description |
|---|---|
| `list_doctors` | List all available doctors and specialties |
| `check_doctor_availability` | Real-time slot availability from Google Calendar |
| `book_appointment` | Creates Google Calendar event + Meet link |
| `lookup_appointments` | Fetch upcoming appointments by patient email |
| `reschedule_appointment` | Moves existing booking to new date/time |
| `cancel_appointment` | Cancels booking and notifies patient |
| `send_confirmation_email` | Resends confirmation to patient email |

---

## Features

- **Real-time voice interaction** — Deepgram WebSocket streaming with VAD (voice activity detection)
- **Barge-in detection** — patient can interrupt the agent mid-sentence
- **Confirmation loop** — agent reads back every detail (email, name, date, time, doctor) before taking any action
- **Natural language dates** — "next Thursday", "tomorrow" converted to YYYY-MM-DD automatically
- **Spoken email parsing** — "john dot smith at gmail dot com" → john.smith@gmail.com
- **Auto confirmation email** — sent instantly after every booking, reschedule, or cancellation
- **Google Meet link** — generated automatically for every appointment

---

## Doctors & Specialties

| Doctor | Specialty |
|---|---|
| Dr. Jay | General Physician |
| Dr. Max | Cardiologist |
| Dr. Kim | Neurologist |
| Dr. Lee | Orthopedic |
| Dr. Mia | Gynecologist |
| Dr. Sam | Dermatologist |
| Dr. Rio | Diabetologist |
| Dr. Ace | ENT Specialist |

---

## Setup

### 1. Clone & create virtual environment

```bash
git clone <repo-url>
cd hospital-agent
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the root directory:

```env
ANTHROPIC_API_KEY=your_anthropic_key
DEEPGRAM_API_KEY=your_deepgram_key
DOCTOR_EMAIL=doctor@example.com
```

### 3. Google Calendar credentials

Place your `credentials.json` (Google OAuth2) in the root directory. On first run, a browser window will open for authentication.

### 4. Run

```bash
python main.py
```

Open **http://localhost:8000** in your browser.

---

## Usage

1. Open **http://localhost:8000**
2. Click **Call** to start a voice session
3. Speak naturally — examples:
   - *"I want to book an appointment with a cardiologist"*
   - *"Check my upcoming appointments"*
   - *"I need to reschedule my appointment to next Friday at 2pm"*
   - *"Cancel my appointment"*
4. Click **End** to end the session or **Clear** to reset conversation history

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `POST` | `/api/chat` | Main conversational AI endpoint |
| `POST` | `/api/tts` | Text-to-speech (Deepgram) |
| `GET` | `/api/deepgram-key` | Fetch Deepgram key for browser STT |
| `GET` | `/api/doctors` | List all doctors |
| `GET` | `/api/doctors/{name}/availability` | Doctor availability by date |
| `POST` | `/api/appointments/book` | Book appointment (direct API) |
| `POST` | `/api/appointments/reschedule` | Reschedule appointment |
| `POST` | `/api/appointments/cancel` | Cancel appointment |
| `POST` | `/api/chat/clear` | Clear conversation session |

---

## Project Structure

```
hospital-agent/
├── main.py                    # FastAPI app entry point
├── app/
│   ├── agents/
│   │   ├── graph.py           # LangGraph pipeline + ReAct orchestrator
│   │   └── appointment.py     # Appointment agent + 7 tools
│   ├── routes/
│   │   ├── chat.py            # /api/chat endpoint
│   │   ├── appointments.py    # Appointment REST endpoints
│   │   ├── tts.py             # Text-to-speech endpoint
│   │   └── transcribe.py      # Transcription endpoint
│   ├── services/
│   │   └── google_meet.py     # Google Calendar + Meet + Gmail integration
│   ├── frontend/
│   │   └── ui.py              # Full voice UI (HTML/CSS/JS)
│   └── data/
│       ├── doctors.json       # Doctor profiles
│       └── packages.json      # Health checkup packages
└── credentials.json           # Google OAuth2 credentials
```
