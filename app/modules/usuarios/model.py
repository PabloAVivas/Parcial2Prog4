from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel, DateTime
from datetime import datetime, timedelta, timezone
## TENEMOS QUE IMPORTAR EL MODELO DE ROL PARA LA RELACION

class UsuarioRol(SQLModel, table=True):
    __tablename__ = 'usuario_rol'

    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    rol_codigo: str = Field(foreign_key="rol.codigo", primary_key=True)
    asignado_por_id: int = Field(foreign_key="usuario.id", nullable=False)
    expires_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True, default=None))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))

class Usuario(SQLModel, table=True):
    __tablename__ = 'usuario'

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=80, nullable=False)
    apellido: str = Field(index=True, max_length=80, nullable=False)
    email: str = Field(index=True, max_length=254, nullable=False, unique=True)
    celular: Optional[str] = Field(max_length=20, default=None)
    password_hash: str = Field(max_length=60, nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True, default=None))

    direcciones: List["DireccionEntrega"] = Relationship(back_populates="usuario")
    roles: List["Rol"] = Relationship(back_populates="usuarios", link_model=UsuarioRol)
    tokens: List["RefreshToken"] = Relationship(back_populates="usuario")

class RefreshToken(SQLModel, table=True):
    __tablename__ = 'refresh_token'

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", nullable=False)
    token_hash: str = Field(max_length=64, nullable=False, unique=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(days=7)))
    revoked_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True, default=None))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    usuario: Usuario = Relationship(back_populates="tokens")

class DireccionEntrega(SQLModel, table=True):
    __tablename__ = 'direccion_entrega'

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", nullable=False)
    alias: Optional[str] = Field(max_length=50)
    linea1: str = Field(nullable=False)
    linea2: Optional[str]
    ciudad: str = Field(max_length=100, nullable=False)
    provincia: str = Field(max_length=100)
    codigo_postal: str = Field(max_length=10)
    latitud: float = Field(sa_column=Column(Numeric(9, 6)))
    longitud: float = Field(sa_column=Column(Numeric(9,6)))
    es_principal: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True, default=None))

