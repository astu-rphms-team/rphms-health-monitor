# RPHMS Short Academic Report

## Abstract

Remote patient monitoring is crucial in modern healthcare because continuous observation helps clinicians detect deterioration early and respond before emergencies occur. This project presents a low-cost Internet of Things (IoT) based health monitoring system named RPHMS, which collects vital signs from patients using an ESP32 microcontroller and biomedical sensors. The system monitors heart rate, blood oxygen saturation (SpO₂), and body temperature, stores the readings in a SQLite database, and displays them on a web dashboard for healthcare staff.

The system uses a FastAPI backend to process incoming sensor data, classify each reading as normal, warning, or critical, and trigger alert events when necessary. Critical readings generate an alert record and can send a Telegram notification to staff. A Groq-powered AI assistant is included to answer operational questions about the live dashboard, while keeping a strict safety boundary that prohibits diagnosis and treatment advice. The project demonstrates a complete end-to-end prototype that combines hardware, software, alerting, and monitoring in a practical and accessible way.

## 1. Introduction

Healthcare systems often depend on periodic patient checks, which may miss sudden changes in a patient’s condition. Continuous monitoring is especially useful for post-operative patients, elderly patients, and individuals with chronic illnesses who require regular observation. Remote monitoring reduces the burden on staff and allows faster response to abnormal conditions.

RPHMS addresses this challenge by combining sensor hardware, a backend service, a database, and a web dashboard into a single monitoring platform. It is designed for demonstration, research, and academic evaluation rather than clinical diagnosis.

## 2. Objectives

The main objectives of this project are:

- to design and implement a remote patient monitoring system using affordable hardware,
- to collect vital signs including heart rate, SpO₂, and temperature,
- to classify readings according to defined thresholds,
- to provide live monitoring through a dashboard,
- to trigger alerts on critical patient conditions,
- to provide optional AI-based assistance for quick operational questions.

## 3. System Design and Architecture

The system is composed of four major layers:

1. Sensor and hardware layer: MAX30102 and DS18B20 sensors connected to an ESP32 device.
2. Communication layer: the ESP32 sends data over Wi-Fi using HTTP requests.
3. Application layer: a FastAPI backend validates, stores, and analyzes the data.
4. Presentation layer: a browser-based dashboard visualizes the patient status and alert information.

The ESP32 sends JSON payloads containing a device ID and vital readings to the backend. The backend matches the device ID to a registered patient and evaluates the reading against configured thresholds. Each vital sign is assigned a status of normal, warning, or critical. The overall status is determined by the most severe category among the three readings.

## 4. Implementation

### Hardware Implementation

The hardware setup includes an ESP32 microcontroller, a MAX30102 pulse oximeter, and a DS18B20 temperature sensor. These sensors capture clinically relevant patient information and send it to the backend at periodic intervals. The firmware is organized in stages to simplify testing and debugging: Wi-Fi connectivity, temperature sensor validation, pulse oximeter validation, and final integrated firmware.

### Backend Implementation

The backend is implemented with Python and FastAPI. It provides endpoints for user login, patient management, vital ingestion, alert handling, summary generation, and AI-assisted queries. Data is stored in SQLite, which keeps the system lightweight and easy to run without a separate database server.

### Frontend Implementation

The frontend is served from the backend static directory using plain HTML, CSS, and JavaScript. It displays patient cards, summary counts, and alert logs. Users can search, filter, sort, and export vital history. A patient detail page provides time-series charts and statistical summaries.

## 5. Alerting and AI Features

The system classifies readings based on threshold ranges defined in the backend. If a reading becomes critical, the backend creates an alert record and optionally dispatches a Telegram message. The web dashboard also displays a banner, toast message, and alert sound to notify staff immediately.

The AI assistant is implemented as a server-side proxy to Groq. It receives the live dashboard context and responds to operational questions such as which patients are critical or which devices are offline. Its system prompt explicitly prevents diagnosis or medical advice, making it a support tool rather than a clinical decision-maker.

## 6. Testing and Evaluation

The project was tested in stages. The firmware was validated step by step using separate Wi-Fi, temperature, and pulse oximetry test sketches before the complete firmware was uploaded. The backend API was validated through Swagger UI and manual HTTP requests, while the frontend was checked for login, registration, status updates, alert acknowledgement, and CSV export functionality. The simulation script also allowed testing without physical hardware.

## 7. Challenges and Limitations

This project has several limitations. First, the sensor readings are intended for monitoring and demonstration rather than clinical-grade accuracy. Second, the security model is suitable for a local demo but would need stronger protection in real deployment. Third, the AI assistant is limited to dashboard summarization and cannot replace professional clinical judgment.

## 8. Conclusion

RPHMS demonstrates how an affordable IoT system can be used for remote patient monitoring. By combining sensor hardware, a web dashboard, alert logic, and AI support, the project provides a realistic end-to-end monitoring workflow. Although it is not a medical diagnostic device, it is a useful academic prototype for health monitoring and early warning systems.

The project successfully shows the complete pipeline from data collection to storage, analysis, alerting, and presentation, making it a strong example of practical IoT-based healthcare innovation.
