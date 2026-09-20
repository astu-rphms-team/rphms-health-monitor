# RPHMS — Integrated IoT-Based Remote Health Monitoring System

ESP32 + sensors → FastAPI backend → SQLite → web dashboard, with Telegram
alerts on critical vitals and a Groq-powered AI assistant.

> This system is for health monitoring and alerting only. It is **not** a
> medical diagnostic device and must not be used to make clinical decisions.

## Team

Adama Science and Technology University — Software Engineering (SE) &
Computer Science and Engineering (CSE).

| #   | Name                    | ID           | Program | Section |
| --- | ----------------------- | ------------ | ------- | ------- |
| 1   | Ermias Taye Gulilat     | UGE/24099/13 | SE      | 1       |
| 2   | Edidia Tamene Gobena    | UGE/24104/13 | SE      | 1       |
| 3   | Hayat Habiba Dilgeba    | UGE/24098/13 | SE      | 1       |
| 4   | Meseret Legesse Wakjira | UGE/24327/13 | SE      | 1       |
| 5   | Sena Goshime Negash     | UGE/24116/13 | SE      | 1       |
| 6   | Ruth Eshetu             | UGE/27811/14 | CSE     | —       |
| 7   | Ayano Tibeso            | UGE/27824/14 | CSE     | —       |
| 8   | Eyob Mulugeta           | UGE/27813/14 | CSE     | —       |
| 9   | Metiol Alemayehu        | UGE/27815/14 | CSE     | —       |
| 10  | Zelalem Endale          | UGE/27821/14 | CSE     | —       |

## Folder structure

```
RPHMS/
├── backend/           # FastAPI app + web dashboard (run this first)
│   └── static/        # The frontend: HTML, CSS, JS
├── firmware/          # ESP32 sketches (4 staged tests)
├── database/          # Reference SQL schema
├── docs/              # Architecture, API reference, report outline
└── README.md
```

## Full project documentation

The complete project documentation is available here:

- [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md)

It includes the system overview, architecture, API details, database design, setup instructions, firmware guide, security considerations, and future work.

## Backend setup

### 1. Requirements

Python 3.10+ and VS Code (recommended).

### 2. Virtual environment

From the `backend/` folder:

```bash
cd backend
python -m venv venv
```

Activate it:

- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (cmd):** `venv\Scripts\activate.bat`
- **Mac/Linux:** `source venv/bin/activate`

Your prompt should now show `(venv)`.

> If PowerShell blocks the script, run once:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional configuration

```bash
cp .env.example .env
```

Fill in Telegram and/or Groq keys (both optional — see sections below).

### 5. Run

**Important: run this from inside the `backend/` folder.**

```bash
uvicorn main:app --reload
```

You should see:

```
[startup] Created default admin user -> username: admin | password: admin123
INFO:     Uvicorn running on http://0.0.0.0:8000
```

`rphms.db` is created automatically — that's the whole database, no server
to install.

### 6. Open it

Go to **http://localhost:8000/** and log in with `admin` / `admin123`.

For the interactive API docs, go to **http://localhost:8000/docs**.

## Testing without hardware (device simulator)

If your ESP32 hasn't arrived, run the simulator — it sends realistic vitals
exactly like the real firmware will, including periodic warning and critical
spikes so you can demo the alerting pipeline.

1. Register a patient in the dashboard with device ID `ESP32_001`
2. In a second terminal (with the venv active):
   ```bash
   cd backend
   python simulate_device.py
   ```

Run several copies with different `DEVICE_ID` values to simulate multiple
patients at once.

You can also post a reading manually:

```bash
curl -X POST http://localhost:8000/api/vitals \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_001","heart_rate":140,"spo2":84,"temperature":39.6}'
```

That one triggers CRITICAL status, an alert row, a Telegram message (if
configured), a banner, a toast, and an alert beep on the dashboard.

## Dashboard features

| Feature                          | Where                                   |
| -------------------------------- | --------------------------------------- |
| Dark / light mode (remembered)   | ☾ button, top right                     |
| Search by name, room, or device  | Toolbar above the patient table         |
| Filter by status (incl. offline) | Chips with live counts                  |
| Sort any column                  | Click a column header                   |
| Critical banner + toast + beep   | Fires when a patient _becomes_ critical |
| Mute alert sound                 | 🔔 button, top right                    |
| Pause auto-refresh               | Pause button (useful mid-demo)          |
| Edit / delete a patient          | Hover a table row                       |
| Threshold reference              | Panel below the patient table           |
| Per-patient stats (avg/min/max)  | Patient detail page                     |
| Chart range (20/50/100/300)      | Patient detail page                     |
| Export readings to CSV           | Patient detail page                     |
| Search + acknowledge all alerts  | Alerts page                             |
| AI assistant                     | ✦ button, bottom right (every page)     |

## AI assistant (Groq)

The ✦ button opens a chat panel that receives a **live snapshot of your
dashboard** — patients, vitals, statuses, offline devices, recent alerts —
so it can answer things like "which patients need attention?" or "any
devices offline?". Groq runs open models (Llama 3.3 by default) at very
high inference speed, which is a nice fit for a chat widget that should
feel instant.

**It is deliberately constrained.** Its system prompt forbids diagnosis,
treatment advice, and clinical judgment; asked for those, it redirects to a
qualified clinician. This boundary is the right one for a monitoring tool
and is worth explaining in your defense.

### Enabling it

1. Get a free key at https://console.groq.com/keys
2. Add to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_your-key-here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
3. Restart the backend.

The key stays server-side: the browser calls our own `/api/ai/chat`, which
forwards to Groq. Never put an API key in frontend code.

Without a key the widget still opens and explains it isn't configured —
nothing else is affected.

## Telegram alerts (optional)

1. Message @BotFather on Telegram, create a bot, copy the token.
2. Send your bot any message, then open
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to find your chat ID.
3. Add both to `backend/.env`:
   ```
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=...
   ```

Without these, critical alerts are still saved and shown on the dashboard —
only the phone notification is skipped.

## Connecting a real ESP32 device

See `firmware/README.md` for wiring, libraries, and the staged upload order.
For the network side:

### Option A — Same Wi-Fi (recommended for your defense)

Laptop and ESP32 on the same network. A phone hotspot works well and avoids
campus networks that block device-to-device traffic.

1. Find your laptop's IP — `ipconfig` (Windows) or `ifconfig | grep "inet "`
   (Mac/Linux). Look for something like `192.168.1.42`.
2. Run the backend so it listens on the network:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Allow it through the firewall when Windows prompts.
4. In the firmware, set `SERVER_URL` to `http://192.168.1.42:8000`.
5. Test from your phone's browser on the same Wi-Fi first — if the login
   page loads there, the ESP32 can reach it too.

> Your laptop's IP can change when you reconnect. Re-check with `ipconfig`
> if the ESP32 stops connecting.

### Option B — Remote access via ngrok

If the ESP32 is on a different network:

```bash
ngrok http 8000
```

Use the public URL ngrok prints as `SERVER_URL`. Note the free URL changes
on each restart, so you'd re-flash each time — fine for a one-off demo,
otherwise deploy the backend somewhere with a stable URL.

**For your defense, Option A is strongly recommended** — simpler, no
internet dependency in the exam room, easy to explain.

## Default login

`admin` / `admin123` — created automatically on first run. Change it in
`create_default_admin()` in `main.py`.

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Auth:** bcrypt password hashing + session tokens
- **Alerts:** Telegram Bot API
- **AI assistant:** Groq via a server-side proxy endpoint
- **Frontend:** Plain HTML/CSS/JS, Chart.js (vendored in `static/vendor/`
  so the demo works with no internet)
- **Firmware:** ESP32 (Arduino), MAX30102, DS18B20

## Troubleshooting

**`uvicorn: command not found`** — your virtual environment isn't active.
Activate it (step 2) and re-run `pip install -r requirements.txt`.

**`FileNotFoundError: static/dashboard.html`** — you ran uvicorn from the
wrong folder. `cd backend` first. (Paths are absolute now, so this should
no longer happen.)

**Wrong `main.py` gets imported** — another project on your `PYTHONPATH` is
shadowing it. Run `cd backend` first; if it persists, clear the variable for
that session with `$env:PYTHONPATH = ""`.

**Charts don't render** — make sure `static/vendor/chart.umd.js` exists.
