from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class UnidadMedidaRead(SQLModel):
    nombre: str 
    simbolo: str 
    tipo: str

class ProductoBasicRead(SQLModel):
    id: int
    nombre: str
    precio_base: float
    stock_cantidad: int

class IngredienteCreate(SQLModel):
    nombre: str
    stock_cantidad: Optional[int] = 0
    unidad_medida_id: int
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = False

class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = None
    stock_cantidad: Optional[int] = None
    unidad_medida_id: Optional[int] = None
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None

class IngredienteRead(SQLModel):
    id: int
    nombre: str
    stock_cantidad: int
    unidad_medida: UnidadMedidaRead
    descripcion: str
    es_alergeno: bool
    activo: bool
    created_at: datetime
    updated_at: datetime
    producto_links: Optional[List[ProductoBasicRead]] = []

class IngredientePaginadoResponse(SQLModel):
    total: int
    data: List[IngredienteRead]
