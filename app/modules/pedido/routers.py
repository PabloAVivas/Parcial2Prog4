import json
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, Path, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlmodel import Session
from app.core.database import get_session, engine
from app.core.deps import get_current_active_user, require_role, get_current_user_ws
from app.core.security import decode_access_token
from app.modules.pedido.schemas import PedidoCreate, PedidoRead, PedidoHistorialUpdate
from app.modules.usuarios.schemas import UsuarioRead
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.pedido.services import PedidoService

router = APIRouter()
def get_pedido_service(session: Session = Depends(get_session)) -> PedidoService:
    return PedidoService(session)

SeDe = Annotated[PedidoService, Depends (get_pedido_service)]

@router.post("/", response_model=PedidoRead, status_code=status.HTTP_201_CREATED, summary="Crear un Pedido con sus relaciones")
async def alta_pedido(usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)], pedido: PedidoCreate, session: SeDe) -> PedidoRead:
    return await session.crear(pedido, usuario_actual.id)

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
async def actualizar_pedido(usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)], datos: PedidoHistorialUpdate, session: SeDe, pedido_id: int = Path(gt=0) ) -> PedidoRead:
    return await session.actualizar(pedido_id, datos, usuario_actual.id)

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrado logico de un pedido")
def eliminar_pedido(admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))], session: SeDe, pedido_id: int = Path(gt=0) ) -> None:
    session.borrado_logico(pedido_id)

@router.websocket("/cocina/ws")
async def websocket_endpoint(websocket: WebSocket, usuario_actual: Annotated[UsuarioRead, Depends(get_current_user_ws)], session: SeDe):
    roles = [rol.codigo for rol in usuario_actual.roles]
    rol_asignado = None
    if "ADMIN" in roles:
        rol_asignado = "ADMIN"
    elif "PEDIDOS" in roles:
        rol_asignado = "PEDIDOS"
    elif "CLIENT" in roles:
        rol_asignado = "CLIENT"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede avanzar",
        )
    
    from app.core.websocket import manager
    await manager.connect(websocket, role=rol_asignado, user_id=usuario_actual.id)
    
    if "ADMIN" in roles:
        from app.core.websocket import manager as mgr
        mgr._join_room(websocket, "role:admin")
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            action = msg.get("action")

            if action == "subscribe-order":
                pedido_id = msg.get("pedido_id")
                if not pedido_id or not isinstance(pedido_id, int):
                    continue

                if "ADMIN" not in roles and "PEDIDOS" not in roles:
                    usuario_pedido = await run_in_threadpool(session.autorizacion_pedido, pedido_id, usuario_actual.id)
                    if not usuario_pedido:
                        await websocket.send_json({
                            "event": "ERROR",
                            "data": {"detail": "No autorizado para este pedido"}
                        })
                        continue

                manager.join_order_room(websocket, pedido_id)

                await websocket.send_json({
                    "event": "SUBSCRIBED",
                    "data": {"pedido_id": pedido_id}
                })

            elif action == "unsubscribe-order":
                pedido_id = msg.get("pedido_id")
                if pedido_id and isinstance(pedido_id, int):
                    manager.leave_order_room(websocket, pedido_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
