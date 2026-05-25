from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_active_user
from app.modules.usuarios.schemas import UsuarioRead, DireccionEntregaCreate, DireccionEntregaRead, DireccionEntregaUpdate
from app.modules.usuarios.service import UsuarioService

router = APIRouter()


def get_usuario_service(session: Session = Depends(get_session)) -> UsuarioService:
    return UsuarioService(session)


SeDe = Annotated[UsuarioService, Depends(get_usuario_service)]


@router.post("/", response_model=DireccionEntregaRead, status_code=status.HTTP_201_CREATED, summary="Crear una direccion de entrega")
def crear_direccion(
    direccion_data: DireccionEntregaCreate,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    service: SeDe,
) -> DireccionEntregaRead:
    return service.crear_direccion_entrega(direccion_data, usuario_actual.id)


@router.get("/", response_model=list[DireccionEntregaRead], summary="Obtener direcciones del usuario autenticado")
def obtener_direcciones(
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    service: SeDe,
) -> list[DireccionEntregaRead]:
    return service.obtener_direcciones_entrega(usuario_actual.id, usuario_actual.id)


@router.patch("/{direccion_id}", response_model=DireccionEntregaRead, summary="Actualizar una direccion")
def actualizar_direccion(
    direccion_data: DireccionEntregaUpdate,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    service: SeDe,
    direccion_id: int = Path(gt=0),
) -> DireccionEntregaRead:
    return service.actualizar_direccion_entrega(direccion_id, direccion_data, usuario_actual.id)


@router.patch("/{direccion_id}/principal", response_model=DireccionEntregaRead, summary="Marcar direccion como principal")
def marcar_principal(
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    service: SeDe,
    direccion_id: int = Path(gt=0),
) -> DireccionEntregaRead:
    return service.marcar_direccion_principal(direccion_id, usuario_actual.id)


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una direccion de entrega")
def eliminar_direccion(
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    service: SeDe,
    direccion_id: int = Path(gt=0),
) -> None:
    service.eliminar_direccion_entrega(direccion_id, usuario_actual.id)
