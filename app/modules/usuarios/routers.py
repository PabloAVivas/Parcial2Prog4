from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session
from app.core.database import get_session
from app.modules.usuarios.schemas import UsuarioRegister, UsuarioLogin, UsuarioRead, UsuarioUpdate, DireccionEntregaCreate, DireccionEntregaRead, DireccionEntregaUpdate, Token, AdministrarRol
from app.modules.usuarios.service import UsuarioService

router = APIRouter()
def get_usuario_service(session: Session = Depends(get_session)) -> UsuarioService:
    return UsuarioService(session)

SeDe = Annotated[UsuarioService, Depends(get_usuario_service)]

@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, summary="Registrar un nuevo usuario")
def registrar(usuario: UsuarioRegister, session: SeDe) -> UsuarioRead:
    return session.registrar_usuario(usuario)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK, summary="Login de usuario")
def iniciar_sesion(usuario: UsuarioLogin, session: SeDe) -> Token:
    return session.login_usuario(usuario)

@router.get("/", model_response= list[UsuarioRead], status_code=status.HTTP_200_OK, summary="Obtener todos los usuarios")
def obtener_lista_usuarios(session: SeDe) -> list[UsuarioRead]:
    return session.obtener_usuarios()

@router.get("/{usuario_id}", model_response= UsuarioRead, status_code=status.HTTP_200_OK, summary="Obtener un usuario por ID")
def obtener_usuario(session:SeDe, usuario_id: int = Path(gt=o)) -> UsuarioRead:
    return session.obtener_usuario_por_id(usuario_id)

@router.patch("/{usuario_id}", model_response= UsuarioRead, status_code=status.HTTP_200_OK, summary="Actualizar un usuario")
def actualizar(session: SeDe, usuario_data: UsuarioUpdate, usuario_id: int = Path(gt=0)) -> UsuarioRead:
    return session.actualizar_usuario(usuario_id, usuario_data)

@router.post("/direccion", response_model=DireccionEntregaRead, status_code=status.HTTP_201_CREATED, summary="Crear una direccion de entrga")
def crear_direccion(session: SeDe, direccion_data: DireccionEntregaCreate) -> DireccionEntregaRead:
    return session.crear_direccion_entrega(direccion_data)

@router.get("/direccion/{usuario_id}", response_model= list[DireccionEntregaRead], summary="Obtener las direcciones de un usuario")
def obtener_direcciones(session: SeDe, usuario_id: int = Path(gt=0)) -> list[DireccionEntregaRead]:
    return session.obtener_direcciones_entrega(usuario_id)

@router.patch("/direccion/{direccion_id}", response_model=DireccionEntregaRead, status_code=status.HTTP_200_OK, summary="Actualizar una direccion del usuario")
def actualizar_direccion(session: SeDe, direccion_data: DireccionEntregaUpdate, direccion_id: int = Path(gt=0)) -> DireccionEntregaRead:
    return session.actualizar_direccion_entrega(direccion_id, direccion_data)

@router.delete("/direccion/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una direccion de entrega de un usuario")
def eliminar_direccion(session: SeDe, direccion_id: int = Path(gt=0)) -> None:
    return session.eliminar_direccion_entrega(direccion_id)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar un usuario")
def desactivar(session: SeDe, usuario_id: int = Path(gt=0)) -> None:
    return session.desactivar_usuario(usuario_id)

@router.patch("/{admin_id}/Asignar", status_code=status.HTTP_200_OK, summary="Asignar un rol a un usuario")
def administrar_roles(session: SeDe, informacion: AdministrarRol, admin_id: int = Path(gt=0)) -> None:
    return session.asignar_rol(admin_id, informacion)

@router.patch("/{admin_id}/remover", status_code=status.HTTP_200_OK, summary="Remover un rol a un usuario")
def remover_rol(session: SeDe, informacion: AdministrarRol, admin_id: int = Path(gt=0)) -> None:
    return session.remover_rol(admin_id, informacion)

