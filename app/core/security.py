from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import Settings


def create_access_token(settings: Settings, subject: str = "admin") -> tuple[str, int]:
    expires_in = settings.JWT_EXPIRE_MINUTES * 60
    expire = datetime.now(UTC) + timedelta(seconds=expires_in)
    payload = {"sub": subject, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_in


def decode_access_token(settings: Settings, token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
