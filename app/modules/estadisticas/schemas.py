from typing import Optional, List
from sqlmodel import SQLModel
from datetime import date

class Periodo(SQLModel):
    desde: date
    hasta: date
    agrupacion: Optional[str] = None

class ResumenResponse(SQLModel):
    ventas_hoy: float
    ticket_promedio: int
    pedidos_activos: int
    mes_actual: int

class VentasPeriodoItem(SQLModel):
    fecha_grupo: date
    cantidad_pedidos: int
    ventas_totales:float

class ProductoTopItem(SQLModel):
    nombre: str
    total_ingresos: float
    cantidad_vendida: int

class PedidosEstadoItem(SQLModel):
    estado_codigo: str
    cantidad: int

class IngresosResponse(SQLModel):
    forma_pago_codigo: str
    cantidad: float