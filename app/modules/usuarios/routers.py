from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path, Response
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.core.unit_of_work import get_uow
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.usuarios.schemas import UsuarioRegister, UsuarioLogin, UsuarioRead, UsuarioUpdate, DireccionEntregaCreate, DireccionEntregaRead, DireccionEntregaUpdate, Token, AdministrarRol
from app.modules.usuarios.service import UsuarioService

router = APIRouter()
def get_usuario_service(session: Session = Depends(get_session)) -> UsuarioService:
    return UsuarioService(session)

def get_usuario_uow(session: Session = Depends(get_session)) -> UsuarioUnitOfWork:
    return UsuarioUnitOfWork(session)

SeDe = Annotated[UsuarioService, Depends(get_usuario_service)]

@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, summary="Registrar un nuevo usuario")
def registrar(usuario: UsuarioRegister, session: SeDe) -> UsuarioRead:
    return session.registrar_usuario(usuario)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK, summary="Login de usuario")
def iniciar_sesion(
    usuario_data: UsuarioLogin,
    service: SeDe,
    response: Response) -> Token:
    token = service.login_usuario(usuario_data)

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False
    )
    return Token.model_validate(token)
    
@router.post("/logout", status_code=status.HTTP_200_OK, summary="Logout de usuario")
def read_me(
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    service: SeDe,
    response: Response
):
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=0,
        samesite="lax",
        secure=False
    )

    service.revocar_refresh_token(usuario_actual.id)
    return None

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
    roles = [rol.codigo for rol in usuario_actual.roles]
    if "ADMIN" not in roles and usuario_actual.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permisos para acceder a este recurso"
        )
    return session.obtener_usuario_por_id(usuario_id)

@router.patch("/{usuario_id}", response_model= UsuarioRead, status_code=status.HTTP_200_OK, summary="Actualizar un usuario")
def actualizar(
    session: SeDe,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    usuario_data: UsuarioUpdate,
    usuario_id: int = Path(gt=0)) -> UsuarioRead:
    roles = [rol.codigo for rol in usuario_actual.roles]
    if "ADMIN" not in roles and usuario_actual.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permisos para acceder a este recurso"
        )
    return session.actualizar_usuario(usuario_id, usuario_data)

@router.post("/direccion", response_model=DireccionEntregaRead, status_code=status.HTTP_201_CREATED, summary="Crear una direccion de entrga")
def crear_direccion(
    session: SeDe,
    direccion_data: DireccionEntregaCreate,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)]) -> DireccionEntregaRead:
    return session.crear_direccion_entrega(direccion_data, usuario_actual.id)

@router.get("/direccion/{usuario_id}", response_model= list[DireccionEntregaRead], summary="Obtener las direcciones de un usuario")
def obtener_direcciones(
    session: SeDe,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    usuario_id: int = Path(gt=0)) -> list[DireccionEntregaRead]:
    if usuario_actual.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permisos para acceder a este recurso"
        )
    return session.obtener_direcciones_entrega(usuario_id)

@router.patch("/direccion/{direccion_id}", response_model=DireccionEntregaRead, status_code=status.HTTP_200_OK, summary="Actualizar una direccion del usuario")
def actualizar_direccion(
    session: SeDe,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    direccion_data: DireccionEntregaUpdate,
    direccion_id: int = Path(gt=0)) -> DireccionEntregaRead:
    return session.actualizar_direccion_entrega(direccion_id, direccion_data, usuario_actual.id)

@router.delete("/direccion/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una direccion de entrega de un usuario")
def eliminar_direccion(
    session: SeDe,
    usuario_actual: Annotated[UsuarioRead, Depends(get_current_active_user)],
    direccion_id: int = Path(gt=0)) -> None:
    return session.eliminar_direccion_entrega(direccion_id, usuario_actual.id)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar un usuario")
def desactivar(
    session: SeDe, 
    admin: Annotated[UsuarioRead, Depends(require_role(["ADMIN"]))],
    usuario_id: int = Path(gt=0)):
        return session.desactivar_usuario(usuario_id)



