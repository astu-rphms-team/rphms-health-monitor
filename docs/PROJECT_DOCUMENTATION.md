# RPHMS Complete Project Documentation

## 1. Project Overview

The Remote Patient Health Monitoring System (RPHMS) is an IoT-based health monitoring platform that collects patient vital signs from ESP32 devices, stores them in a database, processes alert conditions, and presents live monitoring data through a web dashboard. The system supports patient registration, real-time dashboard summaries, threshold-based alerting, Telegram notifications, and a Groq-powered AI assistant for operational questions.

This project is designed as a demonstration and academic prototype for remote monitoring. It is intended for monitoring and alerting only and must not be treated as a medical diagnostic system.

> Important: RPHMS is not a medical diagnosis tool and must not replace clinical judgment or professional medical advice.

## 2. Problem Statement

Healthcare providers often need a way to monitor patients remotely without constant bedside observation. In many situations, especially during recovery or chronic monitoring, a patient’s condition may require a system that continuously tracks vital signs, raises alerts when values fall outside safe ranges, and gives staff a quick view of the patient status.

RPHMS addresses this need by combining:

- wearable or bedside sensor hardware,
- an ESP32 microcontroller for data acquisition,
- a Python FastAPI backend for processing and storage,
- a real-time dashboard for monitoring,
- alerting through Telegram,
- a simple AI assistant for operational guidance.

## 3. Project Goals

The system aims to:

- collect heart rate, oxygen saturation, and temperature data,
- classify each reading as normal, warning, or critical,
- persist readings and alert events to a local database,
- support patient registration and management,
- display live patient status in a web dashboard,
- trigger alerts on critical events,
- provide optional AI-based summaries for dashboard questions,
- remain simple to run locally without a complex infrastructure.

## 4. Functional Scope

### Core Features

- ESP32-based data collection from MAX30102 and DS18B20 sensors
- REST API for patient, vitals, and alert management
- SQLite database with automatic table creation
- Patient registration and tracking by device ID
- Threshold logic for vital sign classification
- Real-time dashboard with status chips, search, sorting, and filters
- Alert history with acknowledgement tracking
- Telegram push notification support for critical events
- AI assistant powered by Groq using live dashboard context
- CSV export of patient readings
- Local HTML/CSS/JS dashboard with no Node.js build system

## 5. Non-Functional Requirements

The project was designed around a few practical engineering constraints:

- easy local setup for demonstration,
- zero external database service requirement,
- no internet dependency for the local UI,
- low cost and accessible hardware,
- simple codebase suitable for academic study,
- support for simulation when hardware is unavailable.

## 6. System Architecture

### High-Level Design

```text
Sensors (MAX30102, DS18B20)
        |
        v
   ESP32 Device
        |
        | Wi-Fi / HTTP
        v
FastAPI Backend
  - Auth
  - Patient API
  - Vitals API
  - Alert logic
  - AI assistant proxy
        |
        +--> SQLite Database
        |
        +--> Dashboard Frontend
        |
        +--> Telegram Alert Service
        |
        +--> Groq API
```

### Layer Responsibilities

#### 1. Hardware Layer

The ESP32 reads sensor values and sends them to the backend over HTTP. In the project, data is sent as JSON including:

- device_id
- heart_rate
- spo2
- temperature

#### 2. Application Layer

The FastAPI backend handles:

- authentication
- patient records
- vital data ingestion
- alert generation
- dashboard summary creation
- threshold evaluation
- AI assistant requests

#### 3. Data Layer

SQLite stores:

- users
- patients
- vitals
- alerts

The database is created automatically when the backend starts for the first time.

#### 4. Presentation Layer

The frontend is a set of HTML, CSS, and JavaScript files served from the backend static directory. It polls the backend periodically to refresh monitoring data and presents patient status visually.

## 7. Technology Stack

### Backend

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- passlib + bcrypt for password hashing
- python-dotenv for environment configuration
- requests for external API calls

### Frontend

- Plain HTML
- CSS
- JavaScript
- Chart.js (vendored locally)

### Hardware

- ESP32 microcontroller
- MAX30102 pulse oximeter sensor
- DS18B20 temperature sensor

### Optional External Services

- Telegram Bot API for notification messages
- Groq API for AI assistant questions

## 8. Project Structure

```text
RPHMS/
├── backend/
│   ├── ai_assistant.py
│   ├── auth.py
│   ├── database.py
│   ├── env.example
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── schemas.py
│   ├── simulate_device.py
│   ├── telegram_alert.py
│   ├── thresholds.py
│   └── static/
│       ├── alerts.html
│       ├── app.js
│       ├── assistant.js
│       ├── dashboard.html
│       ├── login.html
│       ├── patient.html
│       ├── style.css
│       └── vendor/
├── database/
│   └── schema.sql
├── docs/
│   ├── api_reference (3).md
│   ├── architecture (3).md
│   ├── project_report_outline (2).md
│   ├── title_page (2).md
│   └── PROJECT_DOCUMENTATION.md
├── firmware/
│   ├── README.md
│   ├── rphms_firmware.ino
│   ├── stage1_wifi_test.ino
│   ├── stage2_ds18b20_test.ino
│   └── stage3_max30102_test.ino
├── README (3).md
└── .gitignore
```

## 9. Database Design

The database is small but central to the system.

### Tables

#### users

Stores admin or provider login credentials.

Fields:

- id
- username
- password_hash
- name
- created_at

#### patients

Represents a registered patient and links the patient to a connected device.

Fields:

- id
- name
- age
- gender
- device_id
- room_no
- status
- created_at

#### vitals

Stores one sensor reading per record.

Fields:

- id
- patient_id
- heart_rate
- spo2
- temperature
- status
- recorded_at

#### alerts

Stores critical alert events.

Fields:

- id
- patient_id
- message
- acknowledged
- created_at

### Relationship Logic

- Each patient has many vitals.
- Each patient has many alerts.
- device_id is the key that bridges the ESP32 hardware with a patient record.

## 10. Threshold Logic and Status Classification

The threshold configuration is defined in [backend/thresholds.py](../backend/thresholds.py).

### Heart Rate

- Normal: 60–100 bpm
- Warning: 50–120 bpm
- Critical: anything outside warning band

### SpO2

- Normal: 95% and above
- Warning: between 90% and 94%
- Critical: below 90%

### Temperature

- Normal: 36.1°C to 37.5°C
- Warning: 35.5°C to 38.5°C
- Critical: outside that warning band

### Overall Status

The overall status is determined as the most severe of the three measurements. A patient can be normal in heart rate but critical in temperature, and the overall status becomes critical.

## 11. Authentication and Security Model

### Login Flow

The backend creates a default admin user on startup:

- username: admin
- password: admin123

The app uses:

- bcrypt hashing for passwords,
- ephemeral in-memory session tokens,
- Authorization header using Bearer tokens.

### Security Notes

- API keys for Groq and Telegram are kept server-side and never embedded in frontend code.
- The dashboard relies on backend authentication for protected routes.
- The project is intentionally simple and local-demo friendly.

### Production Caveat

For deployment beyond a classroom or demo setting, the project would require:

- HTTPS/TLS
- stronger authentication and role separation
- secure secret storage
- audit logging
- device authentication for ESP32 traffic

## 12. API Overview

The backend exposes a REST API documented by FastAPI at `/docs`.

### Authentication Endpoints

- POST /api/login

### Patient Endpoints

- POST /api/patients
- GET /api/patients
- GET /api/patients/{patient_id}
- PUT /api/patients/{patient_id}
- DELETE /api/patients/{patient_id}

### Vitals Endpoints

- POST /api/vitals
- GET /api/patients/{patient_id}/vitals
- GET /api/patients/{patient_id}/latest
- GET /api/patients/{patient_id}/stats
- GET /api/patients/{patient_id}/export

### Alert Endpoints

- GET /api/alerts
- POST /api/alerts/{alert_id}/acknowledge

### Dashboard Endpoints

- GET /api/dashboard
- GET /api/thresholds

### AI Endpoints

- POST /api/ai/chat

## 13. Request and Response Model

### Example Login Request

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Example Vitals Submission

```json
{
  "device_id": "ESP32_001",
  "heart_rate": 140,
  "spo2": 84,
  "temperature": 39.6
}
```

### Example Response

```json
{
  "id": 12,
  "patient_id": 3,
  "heart_rate": 140,
  "spo2": 84,
  "temperature": 39.6,
  "status": "critical",
  "recorded_at": "2026-09-20T12:00:00"
}
```

## 14. Alerting Behavior

When a reading is classified as critical, the backend:

1. saves the reading to the vitals table,
2. creates a new alert entry,
3. sends a Telegram message if configuration is present,
4. updates the dashboard summary,
5. triggers banner and toast notifications on the web UI.

The system only sends notifications for critical conditions, not for every data point.

## 15. AI Assistant Design

The AI assistant works as a server-side proxy to Groq.

### Purpose

It helps staff ask operational questions such as:

- Which patients need attention?
- Are any devices offline?
- Which patients are in warning status?
- What are the recent alerts?

### Safety Boundary

The assistant is deliberately constrained to avoid diagnosis or treatment advice. Its system prompt explicitly prohibits:

- diagnosis,
- treatment recommendations,
- clinical judgment,
- unsafe medical claims.

If asked for medical advice, it redirects the user to a qualified clinician.

### Setup

Add the following in `backend/.env`:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

If not configured, the assistant simply informs the user that it is not enabled yet.

## 16. Frontend Dashboard Overview

The dashboard presents several live views:

- patient table with filtering and sorting,
- online/offline status indicators,
- vital sign summary cards,
- alert banner and toast notifications,
- patient details with charts,
- AI chat widget,
- alerts management page.

### Main Pages

- /login
- /dashboard.html
- /patient.html
- /alerts.html

### Dashboard Interaction Features

- search by patient name, room, or device ID
- filter by patient status
- sort columns by clicking headers
- mute or enable alert sound
- pause auto-refresh for demos
- open patient detail pages
- export readings in CSV format
- acknowledge alerts

## 17. Firmware and Hardware Details

### Sensor Components

#### MAX30102

Used for pulse oximetry and heart rate estimation.

#### DS18B20

Used for temperature measurement.

### Staged Firmware Development

The project contains staged firmware sketches in this order:

1. stage1_wifi_test.ino
2. stage2_ds18b20_test.ino
3. stage3_max30102_test.ino
4. rphms_firmware.ino

This staged approach helps isolate hardware and network issues before final integration.

### Wiring Summary

- DS18B20 temperature sensor connected to GPIO4 with pull-up resistor
- MAX30102 uses I2C on GPIO21 (SDA) and GPIO22 (SCL)
- Both sensors are powered by 3.3V

### Firmware Upload Sequence

The firmware sends sensor readings to the server every 10 seconds by default.

The ESP32 must be configured with:

```cpp
const char* WIFI_SSID = "...";
const char* WIFI_PASSWORD = "...";
const char* SERVER_URL = "http://YOUR_SERVER_IP:8000";
const char* DEVICE_ID = "ESP32_001";
```

The patient with the matching device_id must exist in the backend before the first reading is sent.

## 18. Setup and Installation Guide

### 1. Prerequisites

- Python 3.10 or newer
- Access to a terminal
- Optional: VS Code
- Optional: ESP32 hardware for real sensor testing

### 2. Create and Activate Virtual Environment

```bash
cd backend
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example env file and edit it if using Telegram or Groq:

```bash
copy env.example .env
```

Example:

```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 5. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- http://localhost:8000/
- http://localhost:8000/docs

### 6. Default Login

- Username: admin
- Password: admin123

## 19. Testing Without Hardware

If the ESP32 is not available, you can simulate sensor data with the project’s simulator.

### Run Simulator

```bash
cd backend
python simulate_device.py
```

This script sends realistic vital readings to the backend and can be run multiple times for different patient IDs.

### Manual Post Example

```bash
curl -X POST http://localhost:8000/api/vitals \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_001","heart_rate":140,"spo2":84,"temperature":39.6}'
```

## 20. Troubleshooting

### Backend does not start

Check that the virtual environment is active and dependencies are installed.

### Static frontend files not found

Run uvicorn from the backend folder. The app resolves file paths relative to the file location.

### Vitals are rejected

Ensure the patient has already been registered with the same device_id.

### Telegram alerts are not sent

Check that TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set correctly in `.env`.

### Groq AI does not answer

Ensure GROQ_API_KEY is valid and the model name is supported by Groq.

### ESP32 cannot connect

Check Wi-Fi credentials, frequency support (2.4 GHz only), and server URL reachability.

## 21. Deployment Notes

### Local Demo Deployment

This is the recommended approach for demonstrations and academic testing.

- run backend on a local machine,
- connect ESP32 to the same Wi-Fi network,
- access dashboard via browser on the same network or localhost.

### Remote Deployment

The project can also be deployed using a public tunnel like ngrok, but this is not the preferred academic demo setup because URLs can change.

## 22. Limitations and Future Improvements

### Current Limitations

- local-only authentication and session handling,
- no device secret validation for ESP32 uploads,
- no HTTPS in the demo mode,
- no production-grade medical validation,
- no role-based authorization,
- AI responses are advisory only and not safety-critical.

### Possible Improvements

- JWT or secure session storage,
- encrypted device registration and signed requests,
- database migration system,
- stronger user authentication,
- deployment with Docker,
- advanced charts and analytics,
- integration with healthcare dashboards or EHR systems,
- more robust sensor calibration and smoothing.

## 23. Project Significance

RPHMS demonstrates how a low-cost monitoring system can be built with accessible hardware and open-source software. It includes the full pipeline from sensor acquisition to visualization and alerting, making it a strong example of an end-to-end IoT health monitoring project.

It is especially suitable for:

- engineering project evaluation,
- system design workshops,
- IoT prototype demonstrations,
- remote patient monitoring studies,
- academic reports and technical presentations.

## 24. Conclusion

RPHMS is a complete prototype of a remote patient monitoring system that blends IoT hardware, a Python web backend, a local database, alerting, and AI-assisted interaction. It is simple to run, defendable in academic settings, and sufficiently realistic to show how sensor data can be converted into actionable monitoring information.

The system is best described as a monitoring and alerting platform rather than a medical diagnostic tool, which is an important boundary that should be clearly communicated in any presentation or deployment.
