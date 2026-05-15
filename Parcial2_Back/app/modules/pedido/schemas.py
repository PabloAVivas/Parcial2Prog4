from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class PedidoCreate(SQLModel):
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    notas: str

class PedidoRead(SQLModel):
    id: int
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    notas: str
    created_at: datetime
    updated_at: datetime

class PedidoUpdate(SQLModel):
    estado_codigo: Optional[str] = None
    forma_pago_codigo: Optional[str] = None
    notas: Optional[str] = None

class HistorialDetallePedidoCreate(SQLModel):
    pedido_id: int
    estado_desde: str
    estado_hasta: str
    motivo: str

class HistorialDetallePedidoRead(SQLModel):
    id: int
    pedido_id: int
    estado_desde: str
    estado_hasta: str
    motivo: str
    created_at: datetime