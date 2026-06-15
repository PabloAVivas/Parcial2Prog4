from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import require_role
from app.modules.estadisticas.schemas import ResumenResponse, VentasPeriodoItem, PedidosEstadoItem, IngresosResponse, Periodo
from app.modules.usuarios.schemas import UsuarioRead
from app.modules.estadisticas.services import EstadisticaService

router = APIRouter()
def get_estadisticas_service(session: Session = Depends(get_session)) -> EstadisticaService:
    return EstadisticaService(session)

SeDe = Annotated[EstadisticaService, Depends(get_estadisticas_service)]

@router.get("/ventas", response_model=list[VentasPeriodoItem], status_code=status.HTTP_200_OK)
def ventas_periodo_router(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))], data: Periodo, session: SeDe) -> list[VentasPeriodoItem]:
    return session.get_ventas_periodo(data)