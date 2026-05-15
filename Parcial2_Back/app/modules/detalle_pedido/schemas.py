from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class DetallePedidoCreate(SQLModel):
    pedido_id: int
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: float
    subtotal_snap: float
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

class DetallePedidoUpdate(SQLModel):
    pedido_id: int
    producto_id: int
    cantidad: int
    personalizacion: List[int]