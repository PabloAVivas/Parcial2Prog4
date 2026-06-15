from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.producto.models import Producto
from app.modules.estadisticas.schemas import ResumenResponse, VentasPeriodoItem, PedidosEstadoItem, IngresosResponse, Periodo, ProductoTopItem
from datetime import datetime, timezone, date, timedelta
from app.modules.producto.unit_of_work import ProductoUnitOfWork
from app.modules.pedido.unit_of_work import PedidoUnitOfWork

class EstadisticaService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_ventas_periodo_sv(self, data: Periodo) -> list[VentasPeriodoItem]:
        agrupacion = data.agrupacion.lower()
        if data.desde > data.hasta or agrupacion not in ("dia", "día", "day", "semana", "week", "mes", "month"):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Fechas o agrupacion incorrectas"
            )
        hasta = data.hasta + timedelta(days=1)
        if agrupacion in ("dia", "día"):
            agrupacion = "day"
        elif agrupacion in ("semana"):
            agrupacion = "week"
        elif agrupacion in ("mes"):
            agrupacion = "month"
        with PedidoUnitOfWork(self._session) as uow:
            ventas_periodo = uow.pedido.get_ventas_periodo(data.desde, hasta, agrupacion)
            result = [VentasPeriodoItem(**v) for v in ventas_periodo]
        return result
    
    def get_pedidos_por_estado_sv(self) -> list[PedidosEstadoItem]:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos_estado = uow.pedido.get_pedidos_por_estado()
            result = [PedidosEstadoItem(**p) for p in pedidos_estado]
        return result
    
    def get_ingresos_por_forma_pago_sv(self, data: Periodo) -> list[IngresosResponse]:
        if data.desde > data.hasta:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Fechas al reves"
            )
        hasta = data.hasta + timedelta(days=1)
        with PedidoUnitOfWork(self._session) as uow:
            ingresos_por_forma_pago = uow.pedido.get_ingresos_por_forma_pago(data.desde, hasta)
            result = [IngresosResponse(**i) for i in ingresos_por_forma_pago]
        return result
    
    def get_result_sv(self) -> ResumenResponse:
        hoy = date.today()
        hasta = hoy + timedelta(days=1)
        mes = datetime.now().month
        
        with PedidoUnitOfWork(self._session) as uow:
            ventas_de_hoy = uow.pedido.get_ventas_hoy(hoy, hasta)
            datos_hoy = ventas_de_hoy[0] if ventas_de_hoy else {"contar_ventas": 0, "cantidad": 0}
            
            cantidad_recaudada = datos_hoy["cantidad"] or 0.0
            cantidad_ventas = datos_hoy["contar_ventas"] or 0
            
            if cantidad_ventas == 0:
                promedio = 0
            else:
                promedio = cantidad_recaudada / cantidad_ventas

            pedidos = uow.pedido.get_pedidos_activo(hoy, hasta)

            result = ResumenResponse(
                ventas_hoy= cantidad_ventas,
                ticket_promedio= promedio,
                pedidos_activos= pedidos,
                mes_actual = mes
            )
        return result
    
    def get_productos_top_sv(self, limit: int) -> list[ProductoTopItem]:
        if limit <= 0 or limit is None:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Limite negativo o inexistente"
            )
        with PedidoUnitOfWork(self._session) as uow:

            productos = uow.detalle_pedido.get_productos_top(limit)

            result = [ProductoTopItem(**p) for p in productos]
        return result