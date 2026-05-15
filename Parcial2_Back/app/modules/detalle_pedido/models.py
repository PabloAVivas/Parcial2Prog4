from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, String
from sqlmodel import Field, Relationship, SQLModel, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.modules.pedido.models import Pedido
    from app.modules.producto.models import Producto

class DetallePedido(SQLModel, table=True):

    __tablename__ = "detalle_pedido"

    pedido_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("pedido.id"),
            primary_key=True,
            nullable=False
        )
    )
    producto_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("producto.id"),
            primary_key=True,
            nullable=False
        )
    )

    cantidad: int = Field(SmallInteger, nullable=False, ge=1)

    nombre_snapshot: str = Field(String(200), nullable=False)
    precio_snapshot: float = Field(ge=0, max_digits=10, decimal_places=2, nullable=False)
    subtotal_snap: float = Field(max_digits=10, decimal_places=2, nullable=False)
    personalizacion: List[Integer]

    activo: bool = Field(nullable=False, default=True)

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))