"""
Pydantic schemas: define the shape of request bodies and API responses.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---------- Auth ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    name: str


# ---------- Patients ----------

class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    device_id: str
    room_no: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    room_no: Optional[str] = None
    status: Optional[str] = None


class PatientOut(BaseModel):
    id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    device_id: str
    room_no: Optional[str]
    status: str

    class Config:
        from_attributes = True


# ---------- Vitals ----------

class VitalIn(BaseModel):
    """This is the payload the ESP32 firmware sends."""
    device_id: str
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None


class VitalOut(BaseModel):
    id: int
    patient_id: int
    heart_rate: Optional[float]
    spo2: Optional[float]
    temperature: Optional[float]
    status: str
    recorded_at: datetime

    class Config:
        from_attributes = True


# ---------- Alerts ----------

class AlertOut(BaseModel):
    id: int
    patient_id: int
    message: str
    acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True
