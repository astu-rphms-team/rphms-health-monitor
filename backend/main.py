"""
RPHMS Backend - FastAPI application.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Then open:
    http://localhost:8000/           -> login page
    http://localhost:8000/docs       -> interactive API docs (Swagger UI)
"""

from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc

from dotenv import load_dotenv
load_dotenv()

from database import Base, engine, get_db
import models
import schemas
import auth
from thresholds import overall_status
from telegram_alert import send_telegram_alert

# Create tables on startup (SQLite file created automatically if missing)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RPHMS - Remote Health Monitoring System")

# Allow the ESP32 / browser to call the API (kept open for a local demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# A device is considered OFFLINE if no reading received in this many seconds
DEVICE_OFFLINE_AFTER_SECONDS = 60


# ---------------------------------------------------------------------------
# Startup: create a default admin user if none exists (username: admin / password: admin123)
# ---------------------------------------------------------------------------
@app.on_event("startup")
def create_default_admin():
    db = next(get_db())
    existing = db.query(models.User).filter(models.User.username == "admin").first()
    if not existing:
        default_user = models.User(
            username="admin",
            password_hash=auth.hash_password("admin123"),
            name="Administrator",
        )
        db.add(default_user)
        db.commit()
        print("[startup] Created default admin user -> username: admin | password: admin123")
    db.close()


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.post("/api/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth.create_session(user.username)
    return schemas.LoginResponse(token=token, name=user.name)


# ---------------------------------------------------------------------------
# Patient routes (require login)
# ---------------------------------------------------------------------------
@app.post("/api/patients", response_model=schemas.PatientOut)
def create_patient(
    payload: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    existing = db.query(models.Patient).filter(models.Patient.device_id == payload.device_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="A patient with this device_id already exists")

    patient = models.Patient(**payload.dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@app.get("/api/patients", response_model=list[schemas.PatientOut])
def list_patients(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Patient).order_by(models.Patient.id).all()


@app.get("/api/patients/{patient_id}", response_model=schemas.PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.put("/api/patients/{patient_id}", response_model=schemas.PatientOut)
def update_patient(
    patient_id: int,
    payload: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient


@app.delete("/api/patients/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"detail": "Patient deleted"}


# ---------------------------------------------------------------------------
# Vitals ingestion (called by the ESP32 - no login required, uses device_id instead)
# ---------------------------------------------------------------------------
@app.post("/api/vitals", response_model=schemas.VitalOut)
def submit_vitals(payload: schemas.VitalIn, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.device_id == payload.device_id).first()
    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"No patient registered with device_id '{payload.device_id}'. Register the patient first.",
        )

    status = overall_status(payload.heart_rate, payload.spo2, payload.temperature)

    vital = models.Vital(
        patient_id=patient.id,
        heart_rate=payload.heart_rate,
        spo2=payload.spo2,
        temperature=payload.temperature,
        status=status,
    )
    db.add(vital)
    db.commit()
    db.refresh(vital)

    if status == "critical":
        message = (
            f"CRITICAL ALERT - {patient.name} (Room {patient.room_no or 'N/A'}): "
            f"HR={payload.heart_rate}, SpO2={payload.spo2}, Temp={payload.temperature}"
        )
        alert = models.Alert(patient_id=patient.id, message=message)
        db.add(alert)
        db.commit()
        send_telegram_alert(message)

    return vital


@app.get("/api/patients/{patient_id}/vitals", response_model=list[schemas.VitalOut])
def get_patient_vitals(
    patient_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    vitals = (
        db.query(models.Vital)
        .filter(models.Vital.patient_id == patient_id)
        .order_by(desc(models.Vital.recorded_at))
        .limit(limit)
        .all()
    )
    return list(reversed(vitals))  # oldest -> newest, good for charting


@app.get("/api/patients/{patient_id}/latest", response_model=schemas.VitalOut | None)
def get_patient_latest_vital(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Vital)
        .filter(models.Vital.patient_id == patient_id)
        .order_by(desc(models.Vital.recorded_at))
        .first()
    )


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------
@app.get("/api/alerts", response_model=list[schemas.AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Alert).order_by(desc(models.Alert.created_at)).limit(100).all()


@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    db.commit()
    return {"detail": "Alert acknowledged"}


# ---------------------------------------------------------------------------
# Dashboard summary (drives the summary cards + patient table)
# ---------------------------------------------------------------------------
@app.get("/api/dashboard")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    patients = db.query(models.Patient).filter(models.Patient.status == "active").all()

    counts = {"total": len(patients), "online": 0, "normal": 0, "warning": 0, "critical": 0}
    patient_rows = []
    cutoff = datetime.utcnow() - timedelta(seconds=DEVICE_OFFLINE_AFTER_SECONDS)

    for patient in patients:
        latest = (
            db.query(models.Vital)
            .filter(models.Vital.patient_id == patient.id)
            .order_by(desc(models.Vital.recorded_at))
            .first()
        )

        is_online = bool(latest and latest.recorded_at and latest.recorded_at.replace(tzinfo=None) >= cutoff)
        if is_online:
            counts["online"] += 1

        current_status = latest.status if latest else "normal"
        if latest:
            counts[current_status] += 1
        else:
            counts["normal"] += 1

        patient_rows.append({
            "id": patient.id,
            "name": patient.name,
            "room_no": patient.room_no,
            "device_id": patient.device_id,
            "is_online": is_online,
            "heart_rate": latest.heart_rate if latest else None,
            "spo2": latest.spo2 if latest else None,
            "temperature": latest.temperature if latest else None,
            "status": current_status,
            "last_reading_at": latest.recorded_at if latest else None,
        })

    return {"counts": counts, "patients": patient_rows}


# ---------------------------------------------------------------------------
# Serve the plain HTML/CSS/JS frontend from backend/static
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_login_page():
    return FileResponse("static/login.html")


@app.get("/dashboard.html")
def serve_dashboard_page():
    return FileResponse("static/dashboard.html")


@app.get("/patient.html")
def serve_patient_page():
    return FileResponse("static/patient.html")
