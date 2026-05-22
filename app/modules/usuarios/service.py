from datetime import timedelta, timezone, datetime
from sqlmodel import Session
from fastapi import HTTPException, status
from app.core.security import generar_refresh_token, hashear_password, verificar_password, create_access_token
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.usuarios.model import Usuario, RefreshToken, DireccionEntrega, UsuarioRol, Rol
from app.modules.usuarios.schemas import UsuarioRegister, UsuarioLogin, UsuarioRead, UsuarioUpdate, DireccionEntregaCreate, DireccionEntregaRead, DireccionEntregaUpdate, Token, AdministrarRol

class UsuarioService:
    def __init__(self, session: Session):
        self._session = session

    def registrar_usuario(self, usuario_data: UsuarioRegister) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            if uow.usuario.get_by_email(usuario_data.email):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo que se ingresó ya corresponde a un usuario registrado")

            usuario = Usuario(
                nombre = usuario_data.nombre,
                apellido = usuario_data.apellido,
                celular = usuario_data.celular,
                email = usuario_data.email,
                password_hash = hashear_password(usuario_data.password),
                roles = [uow.rol.get_by_codigo("CLIENT")]
            )

            respuesta = UsuarioRead.model_validate(uow.usuario.add(usuario))

            return respuesta

    def login_usuario(self, usuario_data: UsuarioLogin) -> Token:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_email(usuario_data.email)
            if not usuario or not verificar_password(usuario_data.password, usuario.password_hash):
                raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail= "Correo o contraseña incorrectos")

            if not usuario.activo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario se encuentra desactivado, por favor contactese con el soporte para mas informacion")
            
            roles_codigos = [rol.codigo for rol in usuario.roles]
            access_token = create_access_token(data={"sub": usuario.id, "role":roles_codigos})

            refresh_puro, refresh_hash = generar_refresh_token()

            nuevo_refresh_db = RefreshToken(
                usuario_id = usuario.id,
                token_hash = refresh_hash,
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            )

            uow.refresh_token.add(nuevo_refresh_db)

            return Token(
                access_token = access_token,
                refresh_token = refresh_puro,
                token_type = "bearer",
                expires_in = nuevo_refresh_db.expires_at - datetime.now(timezone.utc)
            )
        
    def actualizar_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)

            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            usuario_actualizado = usuario_data.model_dump(exclude_unset=True)

            for field, value in usuario_actualizado.items():
                setattr(usuario, field, value)

            return UsuarioRead.model_validate(uow.usuario.add(usuario))
    
    def obtener_usuarios(self) -> list[UsuarioRead]:
        with UsuarioUnitOfWork(self._session) as uow:
            return uow.usuario.get_all()

    def obtener_usuario_por_id(self, usuario_id: int) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_Not_FOUND, detail="Usuario no encontrado")
            
            return usuario
    
    def crear_direccion_entrega(self, direccion_data: DireccionEntregaCreate) -> DireccionEntregaRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(direccion_data.usuario_id)
            if not usuario: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            direcciones = uow.direcciones.get_all()
            for direccion in direcciones:
                if direccion == direccion_data:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta direccion ya se encuentra registrada")

                if direccion.es_principal and direccion_data.es_principal:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una direccion principal para este usuario")
            
            direccion_nueva = DireccionEntregaRead.model_validate(uow.direcciones.add(direccion_data))

            return direccion_nueva
    
    def obtener_direcciones_entrega(self, usuario_id: int) -> list[DireccionEntregaRead]:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            return uow.direcciones.get_direcciones_by_usuario_id(usuario.id)

    def actualizar_direccion_entrega(self, direccion_id: int, direccion_data: DireccionEntregaUpdate) -> DireccionEntregaRead:
        with UsuarioUnitOfWork(self._session) as uow:
            direccion = uow.direcciones.get_by_id(direccion_id)
            hay_principal = uow.direcciones.get_es_principal(direccion.usuario_id)
            if not direccion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")
            
            if hay_principal and direccion_data.es_principal:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una direccion principal para este usuario")
            
            direccion_actualizada = direccion_data.model_dump(exclude_unset=True)
            for field, value in direccion_actualizada.items():
                setattr(direccion, field, value)

            uow.direcciones.add(direccion)

            return DireccionEntregaRead.model_validate(direccion)
        
    def eliminar_direccion_entrega(self, direccion_id: int) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            direccion = uow.direcciones.get_by_id(direccion_id)
            if not direccion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")
            
            return uow.direcciones.delete(direccion_id)
        
    def asignar_rol(self, admin_id: int, informacion: AdministrarRol) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(informacion.usuario_id)
            rol = uow.rol.get_by_codigo(informacion.codigo_rol)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            if not rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
            if rol in usuario.roles:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya tiene asignado este rol")
            
            return uow.usuarioRol.add(UsuarioRol(
                usuario_id = usuario.id,
                rol_codigo = informacion.codigo_rol,
                asignado_por_id = admin_id,
                expires_at = informacion.expires_at,
                created_at = datetime.now(timezone.utc)
            ))
        
    def quitar_rol(self, admin_id: int, informacion: AdministrarRol) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(informacion.usuario_id)
            rol = uow.rol.get_by_codigo(informacion.codigo_rol)
            usuario_rol = uow.usuarioRol.get_link(informacion.usuario_id, informacion.codigo_rol)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            if not rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
            if not usuario_rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no tiene asignado este rol")
            
            return uow.usuarioRol.delete(usuario_rol.id)
        
    def desactivar_usuario(self, usuario_id: int) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)
            if not usuario: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            if not usuario.activo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya se encuentra desactivado")
            usuario.deleted_at = datetime.now(timezone.utc)
            uow.usuario.add(usuario)
            return uow.usuario.desactivate_usuario(usuario.id)
