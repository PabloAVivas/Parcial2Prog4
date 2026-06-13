from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class UnidadMedidaRead(SQLModel):
    nombre: str 
    simbolo: str 
    tipo: str

class CategoriaBasicCreate(SQLModel):
    id: int
    es_principal: bool

class IngredienteBasicCreate(SQLModel):
    id: int
    cantidad: float
    unidad_medida_id: int
    es_removible: bool

class CategoriaBasicRead(SQLModel):
    id: int
    nombre: str
    es_principal: bool

class IngredienteBasicRead(SQLModel):
    id: int
    nombre: str
    stock_cantidad: int
    es_alergeno: bool
    cantidad: float
    unidad_medida: UnidadMedidaRead
    es_removible: bool

class ProductoCreate(SQLModel):
    nombre: str
    unidad_medida_id: Optional[int] = None
    descripcion: str
    precio_base: float
    imagenes_url: list[str] = []
    stock_cantidad:int
    disponible: Optional[bool] = True
    categorias: List[CategoriaBasicCreate] = []
    ingredientes: List[IngredienteBasicCreate] = []

class ProductoRead(SQLModel):
    id: int
    nombre: str
    descripcion: str
    precio_base: float
    imagenes_url: list[str] = []
    stock_cantidad:int
    categorias: List[CategoriaBasicRead] = []
    ingredientes: List[IngredienteBasicRead] = []
    disponible: bool
    unidad_medida: UnidadMedidaRead
    created_at: datetime
    updated_at: datetime

class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    unidad_medida_id: Optional[int] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes_url: Optional[list[str]] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = True
    categorias: Optional[List[CategoriaBasicCreate]] = None
    ingredientes: Optional[List[IngredienteBasicCreate]] = None

class ProductoDisponibilidadUpdate(SQLModel):
    disponible: bool

class ProductoPaginadoResponse(SQLModel):
    total: int
    data: List[ProductoRead]