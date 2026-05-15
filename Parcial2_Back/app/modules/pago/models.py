from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String
from sqlmodel import Field, Relationship, SQLModel, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.modules.pedido.models import Pedido
    from app.modules.producto.models import Producto

class Pago(SQLModel, table=True):
    __tablename__ = "pago"

    id:Optional[int] = Field(default=None, primary_key=True)

    pedido_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("pedido.id"),
            primary_key=True,
            nullable=False
        )
    )

    mp_payment_id: int = Field(BigInteger, unique=True, nullable=True, default=None)
    mp_status: str = Field(String(30), nullable=False)
    mp_status_detail: str = Field(String(100))
    external_reference: str = Field(String(100), unique=True, nullable=False)
    idempotency_key: str = Field(String(100), unique=True, nullable=False)
    transaction_amount: float = Field(max_digits=10, decimal_places=2, nullable=False)
    payment_method_id: str = Field(String(50))

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))