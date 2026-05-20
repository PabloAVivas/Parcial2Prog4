from passlib.context import CryptContext
from sqlmodel import Session
from .model import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)