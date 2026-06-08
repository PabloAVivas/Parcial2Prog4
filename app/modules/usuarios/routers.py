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




