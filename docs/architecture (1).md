# RPHMS — System Architecture

## 1. Overview

RPHMS (Remote Patient Health Monitoring System) is a 4-layer IoT system:

```
Sensors (MAX30102, DS18B20)
        |
   ESP32 microcontroller  --- Wi-Fi --->  FastAPI backend
        |                                        |
   (reads vitals every                    SQLite database
    10 seconds)                                  |
                                          Web dashboard (browser)
                                                  |
                                        Telegram (critical alerts)
```

**Design principle:** each layer only knows how to talk to the one next
to it. The ESP32 doesn't know about the database or the dashboard — it
only knows how to POST JSON to one API endpoint. The dashboard doesn't
know about the ESP32 at all — it only knows how to call the REST API.
This separation is what let us build and test each piece independently
(and is a good thing to mention if asked about design decisions in your
defense).

## 2. Data flow, step by step

1. **Sensing.** The MAX30102 continuously samples red/IR light reflected
   from a fingertip. The DS18B20 measures temperature via its digital
   1-Wire protocol.
2. **On-device processing.** The ESP32 runs the SparkFun MAX3010x
   library's built-in algorithm (`maxim_heart_rate_and_oxygen_saturation`)
   on a rolling buffer of 100 samples to compute heart rate (bpm) and
   SpO2 (%). This is standard signal processing already implemented in
   the sensor library — we don't reimplement it from scratch.
3. **Transmission.** Every `SEND_INTERVAL_MS` (default 10 seconds), the
   ESP32 packages `{device_id, heart_rate, spo2, temperature}` as JSON
   and sends it via HTTP POST to `/api/vitals` on the backend.
4. **Classification.** The backend looks up which patient owns that
   `device_id`, then classifies the reading against configurable
   thresholds (`thresholds.py`) into `normal`, `warning`, or `critical` —
   the overall status is the *worst* of the three individual vital
   statuses.
5. **Persistence.** The reading (with its computed status) is saved as a
   row in the `vitals` table.
6. **Alerting.** If the overall status is `critical`, a row is added to
   the `alerts` table and a message is pushed to Telegram via the Bot API.
7. **Presentation.** The browser dashboard polls the backend every 4
   seconds (`GET /api/dashboard`) and re-renders the patient table,
   summary counts, and status colors. The patient detail page similarly
   polls `GET /api/patients/{id}/vitals` to redraw the history charts.

## 3. Why these technology choices

| Choice | Reasoning |
|---|---|
| FastAPI over Flask/Django | Automatic interactive API docs (`/docs`) useful for demoing to instructors; async-ready; minimal boilerplate |
| SQLite over MySQL/Postgres | Zero installation — the database is just a file. No separate database server to run, configure, or explain during a defense |
| Plain HTML/CSS/JS over React | No build tooling (Node/npm) required; every teammate can run it identically; simpler to explain the full request/response cycle when asked |
| Polling over WebSockets | Simpler to implement and explain; "the browser asks the server for updates every few seconds" is an easy sentence to say in a defense; sufficient responsiveness (4s) for a monitoring dashboard |
| Session tokens over JWT | No extra library/complexity; sessions are just a token mapped to a username in memory, which is easy to explain and sufficient for a single-server demo |
| Telegram over SMS/Email for alerts | Free, instant, requires no paid API/SMS gateway — ideal for a student project budget |

## 4. Database design

Four tables, kept deliberately minimal:

- **users** — provider/admin login accounts
- **patients** — one row per registered patient, linked to exactly one
  device via `device_id`
- **vitals** — one row per sensor reading (the time-series data driving
  the history charts)
- **alerts** — one row per critical event, with an `acknowledged` flag so
  staff can mark them as handled

`device_id` is the join key between hardware and software: the ESP32
firmware is configured with a `DEVICE_ID` constant, and a patient is
"linked" to a device simply by registering them with that same string as
their `device_id` in the dashboard. This is intentionally simple — no
separate device-pairing flow or device table needed.

## 5. Status classification logic

Thresholds are hardcoded in `backend/thresholds.py` as plain Python
constants (not a database table) so they're easy to find, read, and
justify in a defense — e.g. "heart rate 60-100 bpm is our normal range,
sourced from standard resting adult HR references."

Each vital sign is classified independently, then the **overall status is
the most severe of the three** — e.g. if temperature is critical but
heart rate and SpO2 are normal, the patient's overall status is critical.
This ensures no dangerous single-vital reading gets diluted/hidden by two
normal ones.

## 6. Limitations (good to state proactively in a defense)

- This is a **monitoring and alerting** tool, not a diagnostic one — we
  state this explicitly in the dashboard's UI and it should be repeated
  verbally in your defense.
- SpO2/HR accuracy from a consumer MAX30102 module is not clinically
  validated — motion artifacts and poor finger placement affect readings,
  same as any consumer pulse oximeter.
- Session-based auth without HTTPS is fine for a local/demo deployment
  but would need TLS and a more robust auth scheme (e.g. JWT with
  refresh tokens) for real-world/production use — worth mentioning as a
  "future work" item if asked about production-readiness.
- Polling (rather than push/WebSockets) means up to a 4-second delay
  before a critical reading appears on-screen, though the Telegram alert
  fires immediately server-side regardless.
