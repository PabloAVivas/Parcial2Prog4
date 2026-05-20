from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, event, SmallInteger, inspect
from sqlmodel import Field, Relationship, SQLModel, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.modules.producto.models import Producto



class FormaPago(SQLModel, table=True):

    __tablename__ = "forma_pago"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(80), nullable=False))
    habilitado: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, default=True)
    )



class EstadoPedido(SQLModel, table=True):

    __tablename__ = "estado_pedido"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(80), nullable=False))
    orden: int = Field(sa_column=Column(Integer, nullable=False))
    es_terminal: bool = Field(sa_column=Column(Boolean, nullable=False))



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
    personalizacion: list[int] = Field(default=[], sa_column=Column(JSONB))

    activo: bool = Field(nullable=False, default=True)

    productos: "Producto" = Relationship()

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))



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

    detalle_pedidos: List["DetallePedido"] = Relationship()
    historial_estado: List["HistorialEstadoPedido"] = Relationship()
    
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

    id:Optional[int] = Field(default=None, primary_key=True)

    pedido_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("pedido.id", ondelete="CASCADE"),
            foreign_key=True,
            nullable=False
        )
    )
    estado_desde: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("estado_pedido.codigo"),
            foreign_key=True,
            nullable=False
        )
    )
    estado_hasta: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("estado_pedido.codigo"),
            foreign_key=True,
            nullable=False
        )
    )

    motivo: Optional[str] = Field(default= None)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))