from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.modules.pedido.schemas import PedidoCreate, PedidoRead, PedidoHistorialUpdate
from app.modules.usuarios.schemas import UsuarioRead
from app.modules.pedido.services import PedidoService

router = APIRouter()
def get_pedido_service(session: Session = Depends(get_session)) -> PedidoService:
    return PedidoService(session)

SeDe = Annotated[PedidoService, Depends (get_pedido_service)]

@router.post("/", response_model=PedidoRead, status_code=status.HTTP_201_CREATED, summary="Crear un Pedido con sus relaciones")
def alta_pedido(usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)], pedido: PedidoCreate, session: SeDe) -> PedidoRead:
    return session.crear(pedido, usuario_actual.id)

@router.get("/", response_model= list[PedidoRead], summary="Obtener pedidos")
def listar_pedidos(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN", "PEDIDOS"]))], offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100), session: PedidoService = Depends(get_pedido_service)) -> list[PedidoRead]:
    return session.obtener_todos(offset=offset, limit=limit)

@router.get("/usuario/{usuario_id}", response_model= list[PedidoRead], summary="Obtener pedidos")
def listar_pedidos(usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)], session: PedidoService = Depends(get_pedido_service), usuario_id: int = Path(gt=0)) -> list[PedidoRead]:
    return session.obtener_pedidos_por_usuario(usuario_id, usuario_actual.id)

@router.get("/{pedido_id}", response_model=PedidoRead, summary="Obtener un pedido por id")
def detalle_pedido(usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],session: SeDe, pedido_id: int = Path(gt=0) ) -> PedidoRead:
    return session.obtener_por_id(pedido_id, usuario_actual.id)

@router.patch("/{pedido_id}", response_model=PedidoRead, summary="Actualizar un pedido con sus relaciones")
def actualizar_pedido(usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)], datos: PedidoHistorialUpdate, session: SeDe, pedido_id: int = Path(gt=0) ) -> PedidoRead:
    return session.actualizar(pedido_id, datos, usuario_actual.id)

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrado logico de un pedido")
def eliminar_pedido(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))], session: SeDe, pedido_id: int = Path(gt=0) ) -> None:
    session.borrado_logico(pedido_id)