from typing import Annotated
from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from sqlmodel import Session
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.database import get_session
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UsuarioRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_usuario_uow(session: Session = Depends(get_session)) -> UsuarioUnitOfWork:
    return UsuarioUnitOfWork(session)

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        uow: Annotated[UsuarioUnitOfWork, Depends(get_usuario_uow)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No identificado",
        headers={"WWW-Authenticated" : "Bearer"}
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    usuario_id: int | None = int(payload.get("sub"))
    if usuario_id is None:
        raise credentials_exception
    
    usuario = uow.usuario.get_by_id(usuario_id)
    if usuario is None:
        raise credentials_exception
        
    return UsuarioRead.model_validate(usuario)
    
async def get_current_active_user(
        current_user: Annotated[Usuario, Depends(get_current_user)]
):
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario desactivado"
        )
    
    return UsuarioRead.model_validate(current_user)

def require_role(allowed_roles: list[str]):
    async def role_checker(
            current_user: Annotated[Usuario, Depends(get_current_active_user)]
    ) -> UsuarioRead:
        
        user_roles = [rol.codigo for rol in current_user.roles]
        if not any(rol in allowed_roles for rol in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene el permiso necesario para acceder a este recurso"
            )
        return current_user
    return role_checker

async def get_current_user_ws(
        websocket: WebSocket,
        uow: Annotated[UsuarioUnitOfWork, Depends(get_usuario_uow)]
):
    token = websocket.cookies.get("access_token") 
    
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token faltante")

    payload = decode_access_token(token)
    if payload is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token inválido")
    
    usuario_id: int | None = payload.get("sub")
    if usuario_id is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Usuario no identificado")
    
    usuario = uow.usuario.get_by_id(int(usuario_id))
    if usuario is None or not usuario.activo:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Usuario inactivo o no existe")
        
    return UsuarioRead.model_validate(usuario)