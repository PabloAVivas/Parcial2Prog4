from typing import Annotated
from urllib import response
from fastapi import APIRouter, Depends, status, Response, Request, HTTPException
from sqlmodel import Session
from app.core.rate_limit import limiter
from app.core.database import get_session
from app.core.deps import get_current_active_user
from app.modules.auth.schemas import UsuarioRegister, UsuarioLogin, TokenRead
from app.modules.auth.service import AuthService
from app.modules.usuarios.schemas import UsuarioRead

router = APIRouter()

def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)

SeDe = Annotated[AuthService, Depends(get_auth_service)]

@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, summary="Registrar un nuevo usuario")

@limiter.limit("5/15minutes")
def registrar(request :Request, usuario: UsuarioRegister, session: SeDe) -> UsuarioRead:
    return session.registrar_usuario(usuario)

@router.post("/login", response_model=TokenRead, status_code=status.HTTP_200_OK, summary="Login de usuario")
@limiter.limit("5/15minutes")
def iniciar_sesion(
    request: Request,
    usuario_data: UsuarioLogin,
    service: SeDe,
    response: Response) -> TokenRead:
    token = service.login_usuario(usuario_data)
    
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False
    )
    
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token,
        httponly=True,
        max_age=604800,
        samesite="lax",
        secure=False
    )
    return TokenRead(
        access_token = token.access_token,
        token_type = token.token_type,
        expires_in = 1800)
    
@router.patch("/refresh", response_model=TokenRead, status_code=status.HTTP_200_OK, summary="Refresh de access token")
@limiter.limit("5/15minutes")
def refrescar_token(request: Request, service: SeDe) -> TokenRead:
    refresh_cookie = request.cookies.get("refresh_token")

    if not refresh_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encuentra refresh token en la cookie"
        )
    
    nuevo_access = service.refrescar_access_token(refresh_cookie)
    
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False
    )
    return TokenRead(
        access_token= nuevo_access,
        token_type= "bearer",
        expires_in= 1800
    )

@router.get("/me", response_model=UsuarioRead, summary="Obtener datos del usuario autenticado")
def leer_usuario_actual(
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)]
) -> UsuarioRead:
    return usuario_actual

@router.post("/logout", status_code=status.HTTP_200_OK, summary="Logout de usuario")
def read_me(
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    service: SeDe,
    response: Response
):
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        max_age=0,
        samesite="lax",
        secure=False
    )

    return {'mensaje' : 'Session cerrada correctamente'}