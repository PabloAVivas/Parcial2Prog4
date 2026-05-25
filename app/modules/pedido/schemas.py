from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class DireccionEntregaShort(SQLModel):
    linea1: Optional[str] = None
    linea2: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None

class UsuarioShort(SQLModel):
    nombre: str
    apellido: str
    email: str
    celular: str

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
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None
    created_at: datetime

class PedidoCreate(SQLModel):
    direccion_id: Optional[int] = None
    forma_pago_codigo: str
    descuento: float
    costo_envio: float
    notas: Optional[str] = None
    detalle_pedidos: List[DetallePedidoCreate] = []

class PedidoRead(SQLModel):
    id: int
    usuario_id: int
    direccion_id: Optional[int] = None
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    notas: Optional[str] = None
    activo: bool
    usuario: UsuarioShort
    direccion: Optional[DireccionEntregaShort] = None
    detalle_pedidos: List[DetallePedidoRead] = []
    historial_estado: List[HistorialEstadoPedidoRead] = []
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime

class PedidoHistorialUpdate(SQLModel):
    estado_bool: bool
    motivo: Optional[str] = None