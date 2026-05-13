from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.modules.categoria.models import Categoria
    from app.modules.ingrediente.models import Ingrediente

class ProductoCategoriaLink(SQLModel, table=True):

    __tablename__ = "producto_categoria_link"

    producto_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("producto.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    categoria_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("categoria.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    es_principal: bool = Field(nullable=False, default=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    producto: "Producto" = Relationship(back_populates="categoria_links")
    categoria: "Categoria" = Relationship()

class ProductoIngredienteLink (SQLModel, table=True):

    __tablename__ = "producto_ingrediente_link"

    producto_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("producto.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    ingrediente_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("ingrediente.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    es_removible: bool = Field(nullable=False, default=False)
    producto: "Producto" = Relationship(back_populates="ingrediente_links")
    ingrediente: "Ingrediente" = Relationship()

class Producto(SQLModel, table=True):
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, nullable=False, max_length=150)
    descripcion: str = Field(nullable=True)
    precio_base: float = Field(ge=0, nullable=False, max_digits=10, decimal_places=2)
    imagenes_url: list[str] = Field(default=[], sa_column=Column(JSONB))
    stock_cantidad: int = Field(nullable=False, ge=0, default=0)
    disponible: bool = Field(nullable= False, default=True)
    activo: bool = Field(nullable=False, default=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True, default=None))
    
    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoriaLink,
    )
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="producto_links",
        link_model=ProductoIngredienteLink,
    )

    categoria_links: List[ProductoCategoriaLink] = Relationship(back_populates="producto")
    ingrediente_links: List[ProductoIngredienteLink] = Relationship(back_populates="producto")