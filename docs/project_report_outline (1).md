# RPHMS — Project Report Outline

Use this as a skeleton for your written report / defense slides. Sections
map to what instructors typically expect; fill in the bracketed parts
with your own details.

---

## 1. Title Page
See `docs/title_page.md` for the full title page with your official team
roster (already filled in from your title-submission file) — just add
your advisor's name and submission date. Copy it as the first page of
your written report.

## 2. Abstract (150-250 words)
Summarize: the problem (remote/continuous patient monitoring is
resource-intensive and manual), your solution (ESP32 + sensors + web
dashboard + alerting), and the outcome (a working end-to-end prototype
covering registration, live monitoring, history, and critical alerts).

## 3. Introduction
- **3.1 Background** — why remote health monitoring matters (e.g.
  hospital staff shortages, need for continuous vs. periodic vitals
  checks, relevance to the Ethiopian healthcare context if relevant to
  your program)
- **3.2 Problem statement** — what specifically is hard about manual
  vitals monitoring today
- **3.3 Objectives**
  - General objective: build a working IoT-based remote monitoring
    prototype
  - Specific objectives: (list — sensor integration, backend API,
    dashboard, alerting, etc. — these map directly to the features list
    from your original project brief)
- **3.4 Scope and limitations** — reuse the "Limitations" section from
  `docs/architecture.md`

## 4. Literature Review / Related Work
- Discuss the reference project you started from
  (github.com/roschlynnmichael/Patient-Monitoring-System) — what it did,
  what technology it used (Arduino Mega + NodeMCU, PHP, MySQL)
- Explain what you kept conceptually (sensor → server → dashboard flow)
  vs. what you changed and why (see the "Why these technology choices"
  table in `docs/architecture.md` — this is good material for showing
  independent design decisions, which instructors look for)
- Optionally mention 1-2 other IoT health monitoring papers/projects if
  your course requires a formal literature review

## 5. System Design and Methodology
- **5.1 System architecture** — insert the diagram from
  `docs/architecture.md` section 1
- **5.2 Hardware design** — component list, wiring diagram (see
  `firmware/README.md`), photos of your actual breadboard setup
- **5.3 Software architecture** — the 4-layer breakdown (firmware,
  backend, database, frontend)
- **5.4 Database design** — ER diagram of the 4 tables (see
  `database/schema.sql`), explain relationships
- **5.5 Alerting logic** — explain the threshold classification system
  from `backend/thresholds.py`

## 6. Implementation
- **6.1 Firmware** — describe the staged development approach (Wi-Fi
  test → sensor tests → combined firmware), include code snippets of the
  key sensor-reading and HTTP POST logic
- **6.2 Backend API** — list your REST endpoints (a table is good here:
  method, path, purpose), mention FastAPI's auto-generated `/docs` as a
  development/testing aid
- **6.3 Frontend** — describe the 4 pages (login, dashboard, patient
  detail, alerts), mention the polling-based live update approach
- **6.4 Alerting pipeline** — walk through what happens end-to-end when a
  critical reading occurs

## 7. Testing
Document what you actually tested — this project already has a good
built-in story:
- Backend: describe testing each endpoint via Swagger UI / curl before
  building the frontend on top of it
- Frontend: describe testing login (success + failure), patient
  registration (including duplicate device_id validation), live dashboard
  updates, and the alerts acknowledge flow
- Firmware: describe the staged hardware testing (Stage 1-3 sketches)
- Include screenshots (see the "Screenshots to capture" list below)

## 8. Results and Discussion
- Show the working dashboard with normal/warning/critical patients
- Show a triggered Telegram alert
- Discuss what worked well and what you'd improve with more time (this
  is a normal, expected part of a defense — don't be afraid to name real
  limitations from `docs/architecture.md` section 6)

## 9. Conclusion and Future Work
- Restate that objectives were met
- Future work ideas (pick 2-4, don't over-promise): multi-parameter
  trend prediction, mobile app version, multiple sensors per patient,
  production-grade auth (JWT + HTTPS), deployment to a cloud host for
  true remote access beyond the local network

## 10. References
- The reference GitHub project
- Any datasheets you cite (MAX30102, DS18B20)
- Any textbooks/papers required by your course

## 11. Appendix
- Full source code is in the GitHub repository (link it)
- Full wiring diagram
- Full API endpoint list

---

## Screenshots to capture before your defense

Run through this checklist with the actual system (hardware or
simulator) running, and save each as an image for your report/slides:

1. Login page
2. Dashboard with at least 3 patients showing different statuses
   (normal/warning/critical) — this is your single most important
   screenshot
3. The "Register patient" modal, filled in
4. A patient detail page showing the history charts with real data
5. The Alerts page showing at least one critical alert
6. An alert acknowledged (before/after)
7. FastAPI's `/docs` Swagger UI page — shows your API is well-documented
8. A Telegram message received on your phone (if you set this up)
9. A photo of your physical ESP32 + sensor breadboard setup
10. Serial Monitor output showing a successful sensor reading

## Suggested defense talking points

If asked "why did you choose X technology," your answers are already
written out for you in `docs/architecture.md` section 3 — read through
that once before your defense so you can answer confidently without
notes.

If asked "what would you do differently," section 6 (Limitations) gives
you 3-4 honest, specific answers — much stronger than saying "nothing" or
being caught off guard.
