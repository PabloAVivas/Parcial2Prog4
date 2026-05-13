from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel, DateTime
from sqlalchemy import Column
from app.modules.producto.models import ProductoCategoriaLink
from datetime import datetime, timezone
if TYPE_CHECKING:
    from app.modules.producto.models import Producto

class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(nullable=True, default=None, foreign_key="categoria.id")

    padre: Optional["Categoria"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )

    nombre: str = Field(index=True, unique=True, max_length=100)
    descripcion: str
    imagen_url: str
    activo: bool = Field(nullable= False, default=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True, default=None))

    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoriaLink,
    )