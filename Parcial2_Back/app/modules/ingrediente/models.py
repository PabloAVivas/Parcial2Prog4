from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel, DateTime
from app.modules.producto.models import ProductoIngredienteLink
from datetime import datetime, timezone
if TYPE_CHECKING:
    from app.modules.producto.models import Producto


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=100)
    descripcion: str
    es_alergeno: bool = Field(default=False)
    activo: bool = Field(nullable= False, default=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))
    
    
    producto_links: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model=ProductoIngredienteLink,
    )