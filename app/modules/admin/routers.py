from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import require_role
from app.modules.usuarios.schemas import UsuarioRead, UsuarioPaginadoResponse, AdministrarRol
from app.modules.usuarios.service import UsuarioService

router = APIRouter()


def get_usuario_service(session: Session = Depends(get_session)) -> UsuarioService:
    return UsuarioService(session)


SeDe = Annotated[UsuarioService, Depends(get_usuario_service)]


@router.get("/usuarios", response_model=UsuarioPaginadoResponse, summary="Listar usuarios con paginación y filtro por rol")
def listar_usuarios(
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    service: SeDe,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    rol: str = Query(default=None),
) -> UsuarioPaginadoResponse:
    return service.obtener_usuarios_admin(offset=offset, limit=limit, rol_codigo=rol)


@router.patch("/usuarios/{usuario_id}/roles/asignar", response_model=UsuarioRead, summary="Asignar un rol a un usuario")
def asignar_rol(
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    service: SeDe,
    informacion: AdministrarRol,
) -> UsuarioRead:
    return service.asignar_rol(admin.id, informacion)


@router.patch("/usuarios/{usuario_id}/roles/remover", response_model=UsuarioRead, summary="Remover un rol de un usuario")
def remover_rol(
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    service: SeDe,
    informacion: AdministrarRol,
) -> UsuarioRead:
    return service.quitar_rol(informacion)


@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar un usuario (soft delete)")
def desactivar_usuario(
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    service: SeDe,
    usuario_id: int = Path(gt=0),
) -> None:
    service.desactivar_usuario(usuario_id)
