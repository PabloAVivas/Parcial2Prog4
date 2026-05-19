from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class ProductoBasicRead(SQLModel):
    id: int
    nombre: str
    precio_base: float
    stock_cantidad: int

class CategoriaCreate(SQLModel):
    nombre: str
    descripcion: str
    imagen_url: str
    parent_id: Optional[int] = None

class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None

class CategoriaShort(SQLModel):
    id: int
    nombre: str

class CategoriaRead(SQLModel):
    id: int
    padre: Optional[CategoriaShort] = None
    nombre: str
    descripcion: str
    imagen_url: str
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    productos: List[ProductoBasicRead] = []

class CategoriaPaginadaResponse(SQLModel):
    total: int
    data: List[CategoriaRead]
