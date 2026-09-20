# RPHMS — Project Report Outline

A skeleton for your written report and defense slides. Fill in the
bracketed parts.

---

## 1. Title Page
Use `docs/title_page.md` — the roster is already filled in from your title
submission. Add advisor name and date.

## 2. Abstract (150–250 words)
The problem (continuous vitals monitoring is manual and staff-intensive),
your solution (ESP32 + sensors + web dashboard + alerting), the outcome
(a working end-to-end prototype covering registration, live monitoring,
history, and critical alerts).

## 3. Introduction
- **3.1 Background** — why remote monitoring matters; staff shortages;
  continuous vs periodic checks
- **3.2 Problem statement**
- **3.3 Objectives** — general + specific (map these to your feature list)
- **3.4 Scope and limitations** — reuse `architecture.md` §7

## 4. Literature Review / Related Work
- The reference project
  (github.com/roschlynnmichael/Patient-Monitoring-System): Arduino Mega +
  NodeMCU, PHP, MySQL
- What you kept conceptually (sensor → server → dashboard) vs what you
  changed and why — `architecture.md` §3 is your source here. This section
  is where instructors look for independent design thinking.
- Add 1–2 IoT health monitoring papers if your course requires a formal
  review

## 5. System Design and Methodology
- **5.1 Architecture** — diagram from `architecture.md` §1
- **5.2 Hardware** — components, wiring (`firmware/README.md`), photos of
  your breadboard
- **5.3 Software architecture** — the four layers
- **5.4 Database design** — ER diagram from `database/schema.sql`
- **5.5 Alerting logic** — threshold classification, worst-wins rule
- **5.6 AI assistant design** — why it's constrained against diagnosis
  (`architecture.md` §6)

## 6. Implementation
- **6.1 Firmware** — the staged approach (Wi-Fi → each sensor → combined),
  with code snippets of sensor reading and the HTTP POST
- **6.2 Backend API** — endpoint table from `docs/api_reference.md`;
  mention `/docs` as a development aid
- **6.3 Frontend** — four pages, polling, search/filter/sort, dark mode
- **6.4 Alerting pipeline** — end-to-end walkthrough of a critical reading
- **6.5 AI integration** — server-side proxy so the key never reaches the
  browser (a security point worth making explicitly)

## 7. Testing
- **Backend** — each endpoint via Swagger UI / curl before the frontend
  existed
- **Frontend** — login success and failure, patient registration including
  duplicate device_id rejection, edit flow, live updates, CSV export,
  alert acknowledge
- **Firmware** — staged hardware tests
- Include screenshots (checklist below)

## 8. Results and Discussion
- Dashboard with normal / warning / critical patients side by side
- A triggered Telegram alert
- The AI assistant answering a real question
- What worked, what you'd improve — name real limitations, don't claim none

## 9. Conclusion and Future Work
Pick 2–4: mobile app, more sensors per patient, production auth (JWT +
HTTPS), cloud deployment for true remote access, trend analysis.

## 10. References
Reference project; MAX30102 and DS18B20 datasheets; any required texts.

## 11. Appendix
GitHub link, full wiring diagram, full endpoint list.

---

## Screenshots to capture

1. Login page
2. **Dashboard with 3+ patients at different statuses** — your single most
   important screenshot
3. Register patient modal, filled in
4. Patient detail page with charts and stats
5. Alerts page with a critical alert
6. An alert before/after acknowledging
7. Dark mode (shows UI polish)
8. AI assistant answering a question about live data
9. FastAPI `/docs` Swagger UI
10. Telegram message on your phone
11. Photo of the ESP32 + sensor breadboard
12. Serial Monitor showing a successful reading

## Defense talking points

- **"Why did you choose X?"** — answers are written out in
  `architecture.md` §3. Read it once beforehand.
- **"What would you do differently?"** — §7 gives you 3–4 honest, specific
  answers. Much stronger than "nothing".
- **"Does it diagnose patients?"** — No, deliberately. Explain the
  threshold engine drives alerts, and the AI assistant is explicitly
  blocked from clinical judgment. Knowing *why* you drew that line is the
  strongest thing you can show.
