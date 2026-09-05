"""
RPHMS Device Simulator
=======================
Stands in for real ESP32 hardware so you can demo and test the full system
before your sensors arrive. It sends realistic, slowly-changing vitals to
your backend every few seconds - exactly like the real firmware will.

USAGE:
    1. Make sure your backend is running (uvicorn main:app --reload)
    2. Register a patient in the dashboard with a device_id, e.g. "ESP32_001"
    3. Edit DEVICE_ID and BACKEND_URL below to match
    4. Run:  python simulate_device.py
    5. Watch the dashboard update live

You can run multiple copies of this script (with different DEVICE_ID values,
one per registered patient) to simulate several patients monitoring at once -
just open several terminals.

To simulate a critical event on demand, press Ctrl+C is NOT needed - just
let it run; every ~30 readings it randomly dips into a warning/critical
range for a few readings, then returns to normal, so you can see the full
alerting pipeline (Telegram + dashboard) fire during a demo.
"""

import requests
import random
import time

# ---------------------------------------------------------------------------
# CONFIGURE THESE
# ---------------------------------------------------------------------------
BACKEND_URL = "http://localhost:8000"   # change if backend runs elsewhere
DEVICE_ID = "ESP32_001"                  # must match a patient's device_id
SEND_INTERVAL_SECONDS = 4                # how often to send a reading

# ---------------------------------------------------------------------------

def generate_normal_reading():
    """Realistic resting vitals with small natural variation."""
    return {
        "heart_rate": round(random.uniform(68, 85), 1),
        "spo2": round(random.uniform(96, 99), 1),
        "temperature": round(random.uniform(36.4, 37.1), 1),
    }


def generate_warning_reading():
    return {
        "heart_rate": round(random.uniform(101, 115), 1),
        "spo2": round(random.uniform(91, 94), 1),
        "temperature": round(random.uniform(37.6, 38.2), 1),
    }


def generate_critical_reading():
    return {
        "heart_rate": round(random.uniform(130, 150), 1),
        "spo2": round(random.uniform(78, 88), 1),
        "temperature": round(random.uniform(38.8, 40.0), 1),
    }


def send_reading(vitals: dict):
    payload = {"device_id": DEVICE_ID, **vitals}
    try:
        response = requests.post(f"{BACKEND_URL}/api/vitals", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[{DEVICE_ID}] Sent HR={vitals['heart_rate']} SpO2={vitals['spo2']} "
                  f"Temp={vitals['temperature']} -> status: {data['status']}")
        else:
            print(f"[{DEVICE_ID}] Backend rejected reading ({response.status_code}): {response.text}")
    except requests.RequestException as e:
        print(f"[{DEVICE_ID}] Could not reach backend: {e}")


def main():
    print(f"RPHMS device simulator starting - device_id: {DEVICE_ID}")
    print(f"Sending to {BACKEND_URL}/api/vitals every {SEND_INTERVAL_SECONDS}s")
    print("Press Ctrl+C to stop.\n")

    reading_count = 0
    while True:
        reading_count += 1

        # Mostly normal readings, but periodically simulate a warning or
        # critical event so you can demo the alerting pipeline.
        roll = random.random()
        if reading_count % 30 == 0:
            vitals = generate_critical_reading()
        elif roll < 0.08:
            vitals = generate_warning_reading()
        else:
            vitals = generate_normal_reading()

        send_reading(vitals)
        time.sleep(SEND_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
