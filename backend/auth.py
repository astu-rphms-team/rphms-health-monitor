"""
Simple authentication for RPHMS.

Kept intentionally simple for a university project:
- Passwords are hashed with passlib (bcrypt).
- On login, we generate a random session token and keep it in memory
  (a Python dict). This avoids needing JWT libraries or Redis.
- Restarting the backend logs everyone out, which is fine for a demo.
"""

import secrets
from datetime import datetime, timedelta
from fastapi import Header, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# token -> {"username": str, "expires": datetime}
_sessions: dict[str, dict] = {}

SESSION_LIFETIME_HOURS = 12


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_session(username: str) -> str:
    token = secrets.token_hex(32)
    _sessions[token] = {
        "username": username,
        "expires": datetime.utcnow() + timedelta(hours=SESSION_LIFETIME_HOURS),
    }
    return token


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> models.User:
    """FastAPI dependency: reads 'Authorization: Bearer <token>' header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ", 1)[1]
    session = _sessions.get(token)

    if not session or session["expires"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Session expired, please log in again")

    user = db.query(models.User).filter(models.User.username == session["username"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
