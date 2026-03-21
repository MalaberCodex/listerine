from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_preview_login_token(email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.preview_login_token_expire_minutes)
    payload = {"sub": email, "exp": expire, "purpose": "preview_login"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_preview_login_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None

    if payload.get("purpose") != "preview_login":
        return None

    email = payload.get("sub")
    if not isinstance(email, str) or not email:
        return None
    return email
