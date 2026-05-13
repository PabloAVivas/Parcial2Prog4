from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class CategoriaBasicCreate(SQLModel):
    id: int
    es_principal: bool

class IngredienteBasicCreate(SQLModel):
    id: int
    es_removible: bool

class CategoriaBasicRead(SQLModel):
    id: int
    nombre: str
    es_principal: bool

class IngredienteBasicRead(SQLModel):
    id: int
    nombre: str
    es_alergeno: bool
    es_removible: bool

class ProductoCreate(SQLModel):
    nombre: str
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
    created_at: datetime
    updated_at: datetime


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes_url: Optional[list[str]] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = True
    categorias: Optional[List[CategoriaBasicCreate]] = None
    ingredientes: Optional[List[IngredienteBasicCreate]] = None

class ProductoPaginadoResponse(SQLModel):
    total: int
    data: List[ProductoRead]