from typing import Optional
from sqlmodel import SQLModel
from datetime import datetime

class UsuarioLogin(SQLModel):
    email: str
    password: str

class UsuarioRegister(SQLModel):
    nombre: str
    apellido: str
    celular: str
    email: str
    password: str

class Token(SQLModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class TokenRead(SQLModel):
    access_token: str
    token_type: str
    expires_in: datetime
