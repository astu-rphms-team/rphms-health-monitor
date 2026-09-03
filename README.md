# RPHMS — Integrated IoT-Based Remote Health Monitoring System

A university project: ESP32 + sensors → FastAPI backend → SQLite → Web dashboard,
with Telegram alerts on critical vitals.

> This system is for health monitoring and alerting only. It is **not** a medical
> diagnostic device and must not be used to make clinical decisions.

## Project status
- ✅ Backend (this README) — built and tested
- ⏳ Frontend (HTML/CSS/JS dashboard) — next step
- ⏳ Firmware (ESP32) — after frontend

## Folder structure

```
RPHMS/
├── backend/          # FastAPI app (this is what you run first)
├── firmware/          # ESP32 Arduino sketch (coming later)
├── database/           # Reference SQL schema
├── docs/                 # Architecture notes
└── README.md
```

## Backend setup (do this first)

### 1. Requirements
- Python 3.10+ installed
- VS Code (recommended) with the Python extension

### 2. Create a virtual environment

Open a terminal in the `backend/` folder:

```bash
cd backend
python -m venv venv
```

Activate it:

- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (cmd):** `venv\Scripts\activate.bat`
- **Mac/Linux:** `source venv/bin/activate`

You'll know it worked because your terminal prompt will show `(venv)`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Telegram alerts

```bash
cp .env.example .env
```

Then edit `.env` and fill in `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
(see comments in `telegram_alert.py` for how to get these). You can skip
this for now — the system works fully without it, alerts just won't be
pushed to Telegram (they'll still show on the dashboard).

### 5. Run the backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
[startup] Created default admin user -> username: admin | password: admin123
INFO:     Uvicorn running on http://0.0.0.0:8000
```

A file called `rphms.db` (SQLite database) will appear automatically in
the `backend/` folder — that's your entire database, no server install needed.

### 6. Test it

Open in your browser: **http://localhost:8000/docs**

This is FastAPI's interactive API tester (Swagger UI). Try it in this order:

1. **POST /api/login** → body: `{"username": "admin", "password": "admin123"}` → copy the `token` from the response.
2. Click the **Authorize** button (top right) → paste the token → Authorize.
3. **POST /api/patients** → body:
   ```json
   {"name": "Test Patient", "age": 30, "gender": "Male", "device_id": "ESP32_001", "room_no": "101"}
   ```
4. **POST /api/vitals** (no auth needed — this is what the ESP32 will call) → body:
   ```json
   {"device_id": "ESP32_001", "heart_rate": 75, "spo2": 98, "temperature": 36.8}
   ```
5. **GET /api/dashboard** → you should see your patient with status `"normal"`.
6. Try again with `"heart_rate": 140, "spo2": 80` → status becomes `"critical"` and a row appears in **GET /api/alerts**.

If all 6 steps work, your backend is fully functional.

## Default login
- Username: `admin`
- Password: `admin123`

(Change this later in `main.py`'s `create_default_admin()` function, or add a
"change password" feature if you want to extend the project.)

## Tech stack
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Auth:** bcrypt password hashing + simple session tokens
- **Alerts:** Telegram Bot API
- **Frontend:** Plain HTML/CSS/JS (Chart.js for graphs) — coming next
- **Firmware:** ESP32 (Arduino framework), MAX30102, DS18B20 — coming after frontend
