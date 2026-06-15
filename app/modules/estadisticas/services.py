from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.producto.models import Producto
from app.modules.estadisticas.schemas import ResumenResponse, VentasPeriodoItem, PedidosEstadoItem, IngresosResponse, Periodo
from datetime import datetime, timezone, date
from app.modules.producto.unit_of_work import ProductoUnitOfWork
from app.modules.pedido.unit_of_work import PedidoUnitOfWork

class EstadisticaService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_ventas_periodo(self, data: Periodo) -> list[VentasPeriodoItem]:
        agrupacion = data.agrupacion.lower()
        if data.desde > data.hasta or agrupacion not in ("dia", "día", "day", "semana", "week", "mes", "month"):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Fechas o agrupacion incorrectas"
            )
        if agrupacion in ("dia", "día"):
            agrupacion = "day"
        elif agrupacion in ("semana"):
            agrupacion = "week"
        elif agrupacion in ("mes"):
            agrupacion = "month"
        with PedidoUnitOfWork(self._session) as uow:
            ventas_periodo = uow.pedido.get_ventas_periodo(data.desde, data.hasta, agrupacion)
            result = [VentasPeriodoItem(**v) for v in ventas_periodo]
        return result