from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.modules.usuarios.schemas import UsuarioRead, UsuarioUpdate, AdministrarRol
from app.modules.usuarios.service import UsuarioService

router = APIRouter()
def get_usuario_service(session: Session = Depends(get_session)) -> UsuarioService:
    return UsuarioService(session)

SeDe = Annotated[UsuarioService, Depends(get_usuario_service)]

@router.get("/", response_model=list[UsuarioRead], status_code=status.HTTP_200_OK, summary="Obtener todos los usuarios")
def obtener_lista_usuarios(
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    service: SeDe
) -> list[UsuarioRead]:
    
    return service.obtener_usuarios()

@router.patch("/asignar", status_code=status.HTTP_200_OK, summary="Asignar un rol a un usuario")
def administrar_roles(
    session: SeDe, 
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    informacion: AdministrarRol) -> UsuarioRead:
    return session.asignar_rol(admin.id, informacion)

@router.patch("/remover", status_code=status.HTTP_200_OK, summary="Remover un rol a un usuario")
def remover_rol(
    session: SeDe, 
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    informacion: AdministrarRol) -> None:
    return session.quitar_rol(informacion)

@router.get("/{usuario_id}", response_model= UsuarioRead, status_code=status.HTTP_200_OK, summary="Obtener un usuario por ID")
def obtener_usuario(
    session:SeDe,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    usuario_id: int = Path(gt=0)) -> UsuarioRead:
    
    return session.obtener_usuario_por_id(usuario_id, usuario_actual.id)

@router.patch("/{usuario_id}", response_model= UsuarioRead, status_code=status.HTTP_200_OK, summary="Actualizar un usuario")
def actualizar(
    session: SeDe,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    usuario_data: UsuarioUpdate,
    usuario_id: int = Path(gt=0)) -> UsuarioRead:

    return session.actualizar_usuario(usuario_id, usuario_data, usuario_actual.id)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar un usuario")
def desactivar(
    session: SeDe, 
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    usuario_id: int = Path(gt=0)):
    session.desactivar_usuario(usuario_id)



