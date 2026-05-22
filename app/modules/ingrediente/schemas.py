from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class ProductoBasicRead(SQLModel):
    id: int
    nombre: str
    precio_base: float
    stock_cantidad: int

class UnidadMedidaRead(SQLModel):
    nombre: str
    simbolo: str
    tipo: str

class IngredienteCreate(SQLModel):
    nombre: str
    unidad_medida_id: int
    descripcion: str
    es_alergeno: Optional[bool] = False

class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None

class IngredienteRead(SQLModel):
    id: int
    nombre: str
    descripcion: str
    es_alergeno: bool
    activo: bool
    created_at: datetime
    updated_at: datetime
    producto_links: List[ProductoBasicRead] = []

class IngredientePaginadoResponse(SQLModel):
    total: int
    data: List[IngredienteRead]
