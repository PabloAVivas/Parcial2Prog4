from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, event, BigInteger
from sqlmodel import Field, Relationship, SQLModel, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

class FormaPago(SQLModel, table=True):

    __tablename__ = "forma_pago"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(20), nullable=False))
    habilitado: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, default=True)
    )

    pedidos: List["Pedido"] = Relationship(back_populates="forma_pago")

class EstadoPedido(SQLModel, table=True):

    __tablename__ = "estado_pedido"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(20), nullable=False))
    orden: int = Field(sa_column=Column(Integer, nullable=False))
    es_terminal: bool = Field(sa_column=Column(Boolean, nullable=False))

    pedidos: List["Pedido"] = Relationship(back_populates="estado")

class Pedido(SQLModel, table=True):

    __tablename__ = "pedido"

    id:Optional[int] = Field(default=None, primary_key=True)
    estado_codigo: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("estado_pedido.codigo",),
            nullable=False
        )
    )
    forma_pago_codigo: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("forma_pago.codigo",),
            nullable=False
        )
    )
    subtotal: float = Field(max_digits=10, decimal_places=2, nullable=False)
    descuento: float = Field(default=0.00, max_digits=10, decimal_places=2, nullable=False)
    costo_envio: float = Field(default=50.00, max_digits=10, decimal_places=2, nullable=False)
    total: float = Field(ge=0, max_digits=10, decimal_places=2, nullable=False)

    notas: str
    activo: bool = Field(nullable=False, default=True)

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True, default=None))

SNAPSHOT_FIELDS = {'subtotal', 'descuento', 'costo_envio', 'total'}

@event.listens_for(Pedido, "before_update")
def prevent_snapshot_modification(mapper, connection, target):
    state = inspect(target)
    for attr in state.attrs:
        if attr.key in SNAPSHOT_FIELDS and attr.history.has_changes():
            raise ValueError(f"El campo '{attr.key}' es una snapshot y no puede ser modificado.")
        


class HistorialEstadoPedido(SQLModel, table=True):

    __tablename__ = "historial_estado_pedido"

    id:Optional[int] = Field(BigInteger, default=None, primary_key=True)

    pedido_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("pedido.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    estado_desde: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("estado_pedido.codigo"),
            primary_key=True,
            nullable=False
        )
    )
    estado_hasta: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("estado_pedido.codigo"),
            primary_key=True,
            nullable=False
        )
    )

    motivo: str
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))