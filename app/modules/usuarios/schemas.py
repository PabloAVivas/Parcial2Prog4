from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class DireccionEntregaRead(SQLModel):
    id: int
    alias: Optional[str] = None
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    provincia: str
    es_principal: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

class DireccionEntregaCreate(SQLModel):
    alias: Optional[str] = None
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    provincia: str
    codigo_postal: str
    latitud: float
    longitud: float
    es_principal: bool = False

class DireccionEntregaUpdate(SQLModel):
    alias: Optional[str] = None
    linea1: Optional[str] = None
    linea2: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    es_principal: Optional[bool] = None

class UsuarioUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    celular: Optional[str] = None
    activo: Optional[bool] = None

class RolRead(SQLModel):
    codigo: str
    nombre: str
    descripcion: str

class UsuarioRead(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: str
    celular: str
    direcciones: List[DireccionEntregaRead] = []
    activo: bool
    roles: List[RolRead] = []

class UsuarioPaginadoResponse(SQLModel):
    total: int
    data: list[UsuarioRead]

class AdministrarRol(SQLModel):
    usuario_id: int
    codigo_rol: str
    expires_at: Optional[datetime] = None