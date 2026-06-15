from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import require_role
from app.modules.estadisticas.schemas import ResumenResponse, VentasPeriodoItem, PedidosEstadoItem, IngresosResponse, Periodo, ProductoTopItem
from app.modules.usuarios.schemas import UsuarioRead
from app.modules.estadisticas.services import EstadisticaService
from datetime import date

router = APIRouter()
def get_estadisticas_service(session: Session = Depends(get_session)) -> EstadisticaService:
    return EstadisticaService(session)

SeDe = Annotated[EstadisticaService, Depends(get_estadisticas_service)]

def get_periodo(
    desde: date = Query(...),
    hasta: date = Query(...),
    agrupacion: Optional[str] = Query(None),
) -> Periodo:
    return Periodo(desde=desde, hasta=hasta, agrupacion=agrupacion)

@router.get("/ventas", response_model=list[VentasPeriodoItem], status_code=status.HTTP_200_OK)
def ventas_periodo_router(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],data: Periodo = Depends(get_periodo), session: EstadisticaService = Depends(get_estadisticas_service)) -> list[VentasPeriodoItem]:
    return session.get_ventas_periodo_sv(data)

@router.get("/pedidos-por-estado", response_model=list[PedidosEstadoItem], status_code=status.HTTP_200_OK)
def pedidos_por_estado_router(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))], session: SeDe) -> list[PedidosEstadoItem]:
    return session.get_pedidos_por_estado_sv()

@router.get("/ingresos", response_model=list[IngresosResponse], status_code=status.HTTP_200_OK)
def ingresos_por_forma_pago_router(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))], data: Periodo = Depends(get_periodo), session: EstadisticaService = Depends(get_estadisticas_service)) -> list[IngresosResponse]:
    return session.get_ingresos_por_forma_pago_sv(data)

@router.get("/resumen", response_model=ResumenResponse, status_code=status.HTTP_200_OK)
def result_router(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))], session: SeDe) -> ResumenResponse:
    return session.get_result_sv()

@router.get("/productos-top/{limit}", response_model=list[ProductoTopItem], status_code=status.HTTP_200_OK)
def productos_top_router(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))], session: SeDe, limit: int) -> list[ProductoTopItem]:
    return session.get_productos_top_sv(limit)