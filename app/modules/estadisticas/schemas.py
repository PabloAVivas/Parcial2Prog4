from typing import Optional, List
from sqlmodel import SQLModel
from datetime import date

class Periodo(SQLModel):
    desde: date
    hasta: date
    agrupacion: str

class ResumenResponse(SQLModel):
    ventas_hoy: float
    ticket_promedio: int
    pedidos_activos: int
    mes_actual: date

class VentasPeriodoItem(SQLModel):
    fecha_grupo: date
    cantidad_pedidos: int
    ventas_totales:float

#class ProductoTopItem(SQLModel):

class PedidosEstadoItem(SQLModel):
    estado: str
    cantidad: int

class IngresosResponse(SQLModel):
    forma_pago: int
    cantidad: float