from passlib.context import CryptContext
from sqlmodel import Session
from .model import Usuario
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from jose import JWTError, jwt
import secrets
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)

    to_encode.update({"type": "access", "exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "access":
            return None
        
        return payload
    except JWTError:
        return None
    
def generar_refresh_token() -> tuple[str, str]:
    token_puro = secrets.token_hex(64)

    token_hash = hashlib.sha256(token_puro.encode()).hexdigest()

    return token_puro, token_hash