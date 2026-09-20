# RPHMS — System Architecture

## 1. Overview

```
Sensors (MAX30102, DS18B20)
        |
   ESP32 microcontroller  --- Wi-Fi --->  FastAPI backend
        |                                        |
   (reads vitals every                    SQLite database
    10 seconds)                                  |
                                          Web dashboard (browser)
                                            |            |
                                     Telegram      Groq AI assistant
                                     (critical)    (answers questions)
```

**Design principle:** each layer only talks to its neighbour. The ESP32
doesn't know about the database or dashboard — it only POSTs JSON to one
endpoint. The dashboard doesn't know the ESP32 exists — it only calls the
REST API. That separation is what let each piece be built and tested
independently, and it's a good answer if asked about design decisions.

## 2. Data flow

1. **Sensing** — MAX30102 samples reflected red/IR light; DS18B20 reports
   temperature over 1-Wire.
2. **On-device processing** — the SparkFun library's
   `maxim_heart_rate_and_oxygen_saturation` runs over a 100-sample rolling
   buffer to compute HR and SpO₂. Standard signal processing from the
   sensor library; we don't reimplement it.
3. **Transmission** — every 10s the ESP32 POSTs
   `{device_id, heart_rate, spo2, temperature}` to `/api/vitals`.
4. **Classification** — the backend finds the patient owning that
   `device_id` and classifies the reading against `thresholds.py`. Overall
   status is the **worst** of the three individual vital statuses.
5. **Persistence** — saved to the `vitals` table.
6. **Alerting** — if critical, an `alerts` row is created and a Telegram
   message is pushed.
7. **Presentation** — the dashboard polls `/api/dashboard` every 4s and
   re-renders. New criticals raise a banner, toast, and audible beep.

## 3. Why these technology choices

| Choice | Reasoning |
|---|---|
| FastAPI | Auto-generated interactive docs (`/docs`) for demos; minimal boilerplate |
| SQLite | Zero install — the database is one file; nothing to configure during a defense |
| Plain HTML/CSS/JS | No Node/npm build step; every teammate runs it identically; simpler to explain the request/response cycle |
| Polling, not WebSockets | "The browser asks every few seconds" is easy to say and defend; 4s is plenty for monitoring |
| Session tokens, not JWT | No extra library; a token mapped to a username is easy to explain and fine for one server |
| Telegram for alerts | Free and instant; no paid SMS gateway |
| Groq behind a proxy endpoint | Keeps the API key server-side — putting it in frontend JS would expose it to anyone viewing source |

## 4. Database design

Four tables:

- **users** — provider/admin accounts
- **patients** — one row per patient, linked to one device via `device_id`
- **vitals** — one row per reading (the time-series behind the charts)
- **alerts** — one row per critical event, with an `acknowledged` flag

`device_id` is the join between hardware and software: the firmware has a
`DEVICE_ID` constant, and a patient is "paired" simply by being registered
with that same string. Intentionally simple — no separate device table or
pairing flow.

## 5. Status classification

Thresholds live in `backend/thresholds.py` as plain constants, not database
rows, so they're easy to find and justify (e.g. "60–100 bpm resting adult
HR"). The dashboard displays them in a reference panel so what's on screen
always matches the code.

Each vital is classified independently and the **most severe wins** — a
critical temperature isn't diluted by two normal readings.

## 6. AI assistant boundary

The assistant receives a live dashboard snapshot as context but its system
prompt explicitly forbids diagnosis, treatment advice, and clinical
judgment, redirecting to a clinician instead. This is a deliberate design
decision, not a limitation: a monitoring tool that appears to diagnose would
be actively unsafe.

## 7. Limitations (state these proactively in a defense)

- **Monitoring and alerting only** — not diagnostic. Stated in the UI and
  should be said out loud in the defense.
- **Consumer sensor accuracy** — MAX30102 readings are affected by motion
  and finger placement and are not clinically validated.
- **Auth without HTTPS** — fine for a local demo; production would need TLS
  and a stronger scheme. Good "future work" answer.
- **Polling delay** — up to 4s before a critical reading appears on screen,
  though the Telegram alert fires immediately server-side.
- **AI can be wrong** — it summarises what it's given; it isn't a safety
  mechanism. The threshold engine, not the assistant, drives alerts.
