-- RPHMS Database Schema
-- This file is for reference / manual inspection.
-- The actual tables are created automatically by SQLAlchemy when the backend starts
-- (see backend/database.py + backend/models.py). Running this file by hand is optional.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    device_id TEXT UNIQUE NOT NULL,      -- must match the ESP32's DEVICE_ID
    room_no TEXT,
    status TEXT DEFAULT 'active',        -- active | discharged
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    heart_rate REAL,
    spo2 REAL,
    temperature REAL,
    status TEXT NOT NULL,                -- normal | warning | critical
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    acknowledged INTEGER DEFAULT 0,      -- 0 = false, 1 = true
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
