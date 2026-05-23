from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class DetallePedidoCreate(SQLModel):
    producto_id: int
    cantidad: int
    personalizacion: List[int]

class DetallePedidoRead(SQLModel):
    pedido_id: int
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: float
    subtotal_snap: float
    personalizacion: List[int]
    created_at: datetime

class HistorialEstadoPedidoRead(SQLModel):
    id: int
    pedido_id: int
    estado_desde: Optional[str] = None
    estado_hasta: str
    motivo: Optional[str] = None
    created_at: datetime

class PedidoCreate(SQLModel):
    forma_pago_codigo: str
    descuento: float
    costo_envio: float
    notas: str
    detalle_pedidos: List[DetallePedidoCreate] = []

class PedidoRead(SQLModel):
    id: int
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    notas: str
    detalle_pedidos: List[DetallePedidoRead] = []
    historial_estado: List[HistorialEstadoPedidoRead] = []
    created_at: datetime
    updated_at: datetime

class PedidoHistorialUpdate(SQLModel):
    estado_bool: Optional[bool] = True
    motivo: Optional[str] = None