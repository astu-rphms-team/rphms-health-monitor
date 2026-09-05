# RPHMS — API Reference

Base URL (local): `http://localhost:8000`

All endpoints except `/api/login` and `/api/vitals` require an
`Authorization: Bearer <token>` header, obtained from `/api/login`.

## Authentication

| Method | Path | Purpose | Auth required |
|---|---|---|---|
| POST | `/api/login` | Log in, returns a session token | No |

## Patients

| Method | Path | Purpose | Auth required |
|---|---|---|---|
| POST | `/api/patients` | Register a new patient | Yes |
| GET | `/api/patients` | List all patients | Yes |
| GET | `/api/patients/{id}` | Get one patient | Yes |
| PUT | `/api/patients/{id}` | Update a patient | Yes |
| DELETE | `/api/patients/{id}` | Delete a patient | Yes |

## Vitals

| Method | Path | Purpose | Auth required |
|---|---|---|---|
| POST | `/api/vitals` | Submit a sensor reading (called by ESP32) | No (uses `device_id` instead) |
| GET | `/api/patients/{id}/vitals?limit=50` | Get recent readings for a patient (for charts) | Yes |
| GET | `/api/patients/{id}/latest` | Get the most recent reading for a patient | Yes |

## Alerts

| Method | Path | Purpose | Auth required |
|---|---|---|---|
| GET | `/api/alerts` | List recent alerts (all patients) | Yes |
| POST | `/api/alerts/{id}/acknowledge` | Mark an alert as acknowledged | Yes |

## Dashboard

| Method | Path | Purpose | Auth required |
|---|---|---|---|
| GET | `/api/dashboard` | Summary counts + per-patient live status (drives the main dashboard view) | Yes |

## Example requests

**Login:**
```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Register a patient** (replace TOKEN):
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"Abebe Kebede","age":45,"gender":"Male","device_id":"ESP32_001","room_no":"101"}'
```

**Submit a vitals reading** (this is what the ESP32/simulator sends):
```bash
curl -X POST http://localhost:8000/api/vitals \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_001","heart_rate":75,"spo2":98,"temperature":36.8}'
```

For the full interactive version of this reference (with the ability to
try each endpoint directly in your browser), run the backend and visit:
**http://localhost:8000/docs**
