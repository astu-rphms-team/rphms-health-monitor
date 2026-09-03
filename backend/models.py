"""
SQLAlchemy ORM models for RPHMS.
Four simple tables: users, patients, vitals, alerts.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """Healthcare provider / admin login account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Patient(Base):
    """A registered patient, linked to one ESP32 device."""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    device_id = Column(String, unique=True, nullable=False, index=True)
    room_no = Column(String)
    status = Column(String, default="active")  # active | discharged
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vitals = relationship("Vital", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")


class Vital(Base):
    """One sensor reading (heart rate, SpO2, temperature) for a patient."""
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    heart_rate = Column(Float)
    spo2 = Column(Float)
    temperature = Column(Float)
    status = Column(String, nullable=False)  # normal | warning | critical
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    patient = relationship("Patient", back_populates="vitals")


class Alert(Base):
    """A critical-status event, optionally sent to Telegram."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    message = Column(String, nullable=False)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="alerts")
