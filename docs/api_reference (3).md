# RPHMS — API Reference

Base URL: `http://localhost:8000`

All endpoints except `/api/login` and `/api/vitals` need an
`Authorization: Bearer <token>` header from `/api/login`.

`/api/vitals` is intentionally unauthenticated — the ESP32 identifies
itself by `device_id`. For a real deployment you'd add a device secret.

## Authentication

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/api/login` | Log in, returns session token | No |

## Patients

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/api/patients` | Register a patient | Yes |
| GET | `/api/patients` | List all patients | Yes |
| GET | `/api/patients/{id}` | Get one patient | Yes |
| PUT | `/api/patients/{id}` | Update a patient | Yes |
| DELETE | `/api/patients/{id}` | Delete a patient | Yes |

## Vitals

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/api/vitals` | Submit a reading (ESP32 calls this) | No |
| GET | `/api/patients/{id}/vitals?limit=50` | Recent readings for charts | Yes |
| GET | `/api/patients/{id}/latest` | Most recent reading | Yes |
| GET | `/api/patients/{id}/stats` | Min/max/avg + event counts | Yes |
| GET | `/api/patients/{id}/export` | Download readings as CSV | Yes |

## Alerts

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/api/alerts` | Recent alerts, all patients | Yes |
| POST | `/api/alerts/{id}/acknowledge` | Mark as handled | Yes |

## Dashboard & config

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/api/dashboard` | Summary counts + per-patient live status | Yes |
| GET | `/api/thresholds` | Configured normal/warning/critical ranges | Yes |

## AI assistant

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/api/ai/chat` | Ask Groq about the live dashboard | Yes |

Request body:
```json
{
  "message": "Which patients need attention?",
  "history": [{"role": "user", "content": "..."},
              {"role": "assistant", "content": "..."}]
}
```

The backend attaches the current dashboard state as context before
forwarding to Groq, so the model can answer about real patients.

## Examples

**Login**
```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Register a patient**
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"Abebe Kebede","age":45,"gender":"Male","device_id":"ESP32_001","room_no":"101"}'
```

**Submit a reading (what the ESP32 sends)**
```bash
curl -X POST http://localhost:8000/api/vitals \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_001","heart_rate":75,"spo2":98,"temperature":36.8}'
```

Interactive version of all of this: **http://localhost:8000/docs**
