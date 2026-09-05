# RPHMS — Integrated IoT-Based Remote Health Monitoring System

A university project: ESP32 + sensors → FastAPI backend → SQLite → Web dashboard,
with Telegram alerts on critical vitals.

> This system is for health monitoring and alerting only. It is **not** a medical
> diagnostic device and must not be used to make clinical decisions.

## Team

Adama Science and Technology University — Software Engineering (SE) &
Computer Science and Engineering (CSE) departments.

| # | Name | ID | Program | Section |
|---|---|---|---|---|
| 1 | Ermias Taye Gulilat | UGE/24099/13 | SE | 1 |
| 2 | Edidia Tamene Gobena | UGE/24104/13 | SE | 1 |
| 3 | Hayat Habiba Dilgeba | UGE/24098/13 | SE | 1 |
| 4 | Meseret Legesse Wakjira | UGE/24327/13 | SE | 1 |
| 5 | Sena Goshime Negash | UGE/24116/13 | SE | 1 |
| 6 | Ruth Eshetu | UGE/27811/14 | CSE | — |
| 7 | Ayano Tibeso | UGE/27824/14 | CSE | — |
| 8 | Eyob Mulugeta | UGE/27813/14 | CSE | — |
| 9 | Metiol Alemayehu | UGE/27815/14 | CSE | — |
| 10 | Zelalem Endale | UGE/27821/14 | CSE | — |

## Project status
- ✅ Backend — built and tested
- ✅ Frontend (login, dashboard, alerts, patient detail with charts) — built and tested
- ✅ Firmware (ESP32 + MAX30102 + DS18B20) — code complete, staged test sketches included
- ✅ Device simulator (for testing/demo without hardware) — built and tested

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

## Using the web dashboard

With the backend running (see above), just open your browser to:

**http://localhost:8000/**

1. Log in with `admin` / `admin123`
2. Click **"+ Register patient"** and fill in a name and a `device_id`
   (e.g. `ESP32_001`) — this `device_id` must exactly match what the ESP32
   firmware sends later.
3. The dashboard auto-refreshes every 4 seconds. Once real (or test) vitals
   are posted to `/api/vitals`, the patient row updates live with color-coded
   status.
4. Click a patient's name to see their live vitals and history charts.

### Testing the dashboard without hardware yet

You can simulate the ESP32 by posting vitals manually with curl (run this
in a second terminal while the backend is running):

```bash
curl -X POST http://localhost:8000/api/vitals \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_001","heart_rate":75,"spo2":98,"temperature":36.8}'
```

Change the numbers to trigger warning/critical status, e.g.:
```bash
curl -X POST http://localhost:8000/api/vitals \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_001","heart_rate":140,"spo2":84,"temperature":39.6}'
```
Refresh the dashboard and you should see the row turn red and a new entry
appear under "Recent alerts".

## Tech stack
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Auth:** bcrypt password hashing + simple session tokens
- **Alerts:** Telegram Bot API
- **Frontend:** Plain HTML/CSS/JS, Chart.js (vendored locally in
  `static/vendor/` so the demo works without internet access)
- **Firmware:** ESP32 (Arduino framework), MAX30102, DS18B20

## Testing without hardware (device simulator)

If your ESP32/sensors haven't arrived yet, or you just want to demo the
system quickly, run the included simulator instead of real hardware. It
sends realistic vitals to your backend exactly like the real firmware
will, including occasional warning/critical spikes so you can see the
alerting pipeline fire.

```bash
cd backend
python simulate_device.py
```

Before running it, make sure you've registered a patient in the dashboard
with `device_id` = `ESP32_001` (or edit `DEVICE_ID` at the top of
`simulate_device.py` to match a patient you've already registered). You
can run multiple copies of the script with different device IDs to
simulate several patients at once.

## Connecting a real ESP32 device

Once your hardware and firmware (see `firmware/README.md`) are ready, the
ESP32 needs to reach your backend over the network. There are two ways to
do this, depending on your situation.

### Option A — Same Wi-Fi network (recommended for your defense demo)

This is the simplest and most reliable option: your laptop (running the
backend) and your ESP32 just need to be on the same Wi-Fi network. A
personal mobile hotspot works great for this — it avoids campus/lab Wi-Fi
networks that sometimes block device-to-device traffic.

**1. Find your laptop's local IP address:**

Windows (PowerShell):
```powershell
ipconfig
```
Look for "IPv4 Address" under your active Wi-Fi adapter, e.g. `192.168.1.42`.

Mac/Linux:
```bash
ifconfig | grep "inet "
```

**2. Make sure the backend listens on all network interfaces**, not just
localhost (our `main.py` already does this by default — `--host 0.0.0.0`
is the default when you run `uvicorn main:app --reload`, but double-check
by explicitly running):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**3. Allow the connection through your firewall** (Windows will usually
prompt you the first time — click "Allow"). If it doesn't prompt you,
you may need to add an inbound rule for port 8000 in Windows Defender
Firewall settings.

**4. In your ESP32 firmware**, set:
```cpp
const char* SERVER_URL = "http://192.168.1.42:8000";  // your laptop's IP
```

**5. Test it from another device first** (e.g. your phone, on the same
Wi-Fi): open a browser and go to `http://192.168.1.42:8000/` — if the
login page loads, your ESP32 will be able to reach it too.

> Your laptop's local IP can change each time you reconnect to Wi-Fi
> (unless your router assigns a fixed/static IP to your device). If the
> ESP32 stops connecting after a restart, re-check your IP with `ipconfig`.

### Option B — True remote access (ESP32 on a different network)

If your ESP32 needs to reach the backend from somewhere else entirely
(e.g. a different building, or you want to demo remotely), you need a
public URL. The simplest way for a student project is a tunneling tool
like **ngrok**:

1. Download ngrok from ngrok.com and sign up for a free account.
2. Run your backend normally: `uvicorn main:app --reload`
3. In a separate terminal:
   ```bash
   ngrok http 8000
   ```
4. ngrok prints a public URL like `https://a1b2c3d4.ngrok-free.app` —
   use this as your `SERVER_URL` in the firmware.

> Note: ngrok's free URL changes every time you restart it, so you'll
> need to re-flash the firmware (or better, make `SERVER_URL` easy to
> update) each time. For a one-off demo this is fine; for anything
> longer-term, consider deploying the backend to a free-tier host like
> Render or Railway instead, which gives you a stable public URL.

For your project defense specifically, **Option A (same network) is
strongly recommended** — it's simpler, doesn't depend on internet
connectivity in the exam room, and is easy to explain if asked.
