# RPHMS Presentation Summary

## Presentation Title

An Integrated IoT-Based Remote Health Monitoring System (RPHMS)

## Slide 1: Title Slide

- Project title
- Team members
- Institution
- Course/project context
- Short tagline: "Remote monitoring for early detection and faster response"

## Slide 2: Problem Statement

- Patients need continuous observation
- Manual monitoring is slow and unreliable
- Sudden changes in vital signs may go unnoticed
- Need for early warning and faster intervention

## Slide 3: Objectives

- Monitor heart rate, SpO₂, and temperature
- Detect normal, warning, and critical states
- Store and visualize patient data
- Notify staff when a patient becomes critical
- Build a practical, low-cost monitoring prototype

## Slide 4: System Architecture

- ESP32 collects sensor readings
- Wi-Fi sends data to FastAPI backend
- Backend stores data in SQLite
- Web dashboard displays live patient conditions
- Telegram alerts notify staff
- AI assistant answers operational questions

## Slide 5: Hardware Components

- ESP32 microcontroller
- MAX30102 pulse oximeter
- DS18B20 temperature sensor
- Breadboard and wiring setup
- Staged firmware testing approach

## Slide 6: Software and Backend

- FastAPI backend for APIs and logic
- SQLAlchemy models for patients, vitals, and alerts
- Threshold-based vital classification
- Authentication and session management
- Event logging and CSV export support

## Slide 7: Dashboard Features

- Patient table with search and filtering
- Live online/offline status
- Normal/warning/critical summaries
- Patient detail page with charts and stats
- Alerts page with acknowledge functionality

## Slide 8: Alerting Pipeline

- Sensor reading arrives
- Backend checks threshold conditions
- Patient becomes critical
- Alert record is created
- Telegram notification is sent
- Dashboard shows banner, toast, and alarm

## Slide 9: AI Assistant and Safety

- Groq model uses live dashboard context
- Helps answer operational questions
- Does not diagnose or suggest treatment
- Redirects users to qualified clinicians
- Keeps API key server-side for safety

## Slide 10: Testing and Results

- Firmware tested in stages
- Backend tested with Swagger and curl requests
- Frontend verified with login, patient registration, and alerting flows
- Simulator used for testing without hardware
- Demonstrated live monitoring and alerts

## Slide 11: Challenges and Limitations

- Demo-level security only
- Sensor accuracy is not clinical-grade
- No direct medical diagnosis
- Local deployment instead of full production health infrastructure

## Slide 12: Conclusion

- RPHMS is a practical IoT health monitoring prototype
- It connects hardware, software, alerting, and monitoring
- It helps show how early warning systems can support healthcare
- Future improvements include stronger security, more sensors, and cloud deployment

## Closing Statement

"This project demonstrates a complete and realistic remote patient monitoring workflow using affordable technology and practical alerting logic."
