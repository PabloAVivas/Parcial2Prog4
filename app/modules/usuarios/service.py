from datetime import timedelta, timezone, datetime
from sqlmodel import Session
from fastapi import HTTPException, status
from app.core.security import generar_refresh_token, hashear_password, verificar_password, create_access_token, calcular_hash_token
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.usuarios.models import Usuario, RefreshToken, DireccionEntrega, UsuarioRol, Rol
from app.modules.usuarios.schemas import UsuarioRegister, UsuarioLogin, UsuarioRead, UsuarioUpdate, DireccionEntregaCreate, DireccionEntregaRead, DireccionEntregaUpdate, Token, AdministrarRol

class UsuarioService:
    def __init__(self, session: Session):
        self._session = session

    def _get_or_404(self, uow:UsuarioUnitOfWork, usuario_id:int) -> Usuario:
        usuario = uow.usuario.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={usuario_id} no encontrado",
            )
        return usuario

    def registrar_usuario(self, usuario_data: UsuarioRegister) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            if uow.usuario.get_by_email(usuario_data.email):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo que se ingresó ya corresponde a un usuario registrado")

            rol_cliente = self._session.get(Rol, "CLIENT")
            usuario = Usuario(
                nombre = usuario_data.nombre,
                apellido = usuario_data.apellido,
                celular = usuario_data.celular,
                email = usuario_data.email,
                password_hash = hashear_password(usuario_data.password),
                roles = [rol_cliente]
            )
            uow.usuario.add(usuario)
            usuario_creado = uow.usuario.get_by_id_usuario(usuario.id)
            respuesta = UsuarioRead.model_validate(usuario_creado)

            return respuesta

    def login_usuario(self, usuario_data: UsuarioLogin) -> Token:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_email(usuario_data.email)
            if not usuario or not verificar_password(usuario_data.password, usuario.password_hash):
                raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail= "Correo o contraseña incorrectos")

            if not usuario.activo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario se encuentra desactivado, por favor contactese con el soporte para mas informacion")
            
            roles_codigos = [rol.codigo for rol in usuario.roles]
            access_token = create_access_token(data={"sub": str(usuario.id), "role":roles_codigos})

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
                expires_in = nuevo_refresh_db.expires_at
            )
        
    def refrescar_access_token(self, refresh_puro: str) -> str:

        refresh_has = calcular_hash_token(refresh_puro)

        with UsuarioUnitOfWork(self._session) as uow:

            db_token = uow.refresh_token.get_by_hash(refresh_has)

            if not db_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh Token invalido"
                )
            
            if db_token.revoked_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh Token revocado"
                )
            
            if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh Token expirado"
                )
            
            usuario = uow.usuario.get_by_id(db_token.usuario_id)
            if not usuario or not usuario.activo:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado o inactivo"
                )
            
            roles_codigos = [rol.codigo for rol in usuario.roles]
            nuevo_access_token = create_access_token(data={"sub" : str(usuario.id), "role" : roles_codigos})
            return nuevo_access_token

    def revocar_refresh_token(self, usuario_id: int) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            tokens = uow.refresh_token.get_active_by_usuario(usuario_id)
            for token in tokens:
                token.revoked_at = datetime.now(timezone.utc)
            

    def actualizar_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate, usuario_actual_id: int) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)
            usuario_actual = uow.usuario.get_by_id(usuario_actual_id)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            if usuario.id != usuario_actual.id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes permisos para realizar esta accion")

            usuario_actualizado = usuario_data.model_dump(exclude_unset=True)

            for field, value in usuario_actualizado.items():
                setattr(usuario, field, value)
            uow.usuario.add(usuario)

            usuario_actualizado_completo = uow.usuario.get_by_id_usuario(usuario.id)
            return UsuarioRead.model_validate(usuario_actualizado_completo)
    
    def obtener_usuarios(self) -> list[UsuarioRead]:
        with UsuarioUnitOfWork(self._session) as uow:
            usuarios = uow.usuario.get_activo()
            return [UsuarioRead.model_validate(u) for u in usuarios]

    def obtener_usuario_por_id(self, usuario_id: int, usuario_actual_id: int) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario_actual = self._get_or_404(uow, usuario_actual_id)
            roles = [rol.codigo for rol in usuario_actual.roles]
            usuario = self._get_or_404(uow, usuario_id)
           
            if usuario.id != usuario_actual.id and "ADMIN" not in roles:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usted no tiene los permisos para realizar esta accion")

            return UsuarioRead.model_validate(usuario)
    
    def crear_direccion_entrega(self, direccion_data: DireccionEntregaCreate, usuario_id: int) -> DireccionEntregaRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = self._get_or_404(uow, usuario_id)
            if usuario.id != usuario_id: 
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes permisos para acceder a este recurso"
                )
            
            for direccion in usuario.direcciones:
                if direccion.linea1 == direccion_data.linea1 and direccion.linea2 == direccion_data.linea2:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta direccion ya se encuentra registrada")

                if direccion.es_principal and direccion_data.es_principal:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una direccion principal para este usuario")
            
            direccion_nueva =DireccionEntrega(**direccion_data.model_dump(), usuario_id=usuario_id)
            uow.direccion_entrega.add(direccion_nueva)

            return DireccionEntregaRead.model_validate(direccion_nueva)
    
    def obtener_direcciones_entrega(self, usuario_id: int, usuario_actual_id: int) -> list[DireccionEntregaRead]:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario_actual = uow.usuario.get_by_id(usuario_actual_id)
            usuario = uow.usuario.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            if usuario_actual.id != usuario.id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes permisos para acceder a este recurso")

            direcciones = uow.direccion_entrega.get_direcciones_by_usuario_id(usuario_id)
            lista_direcciones = [DireccionEntregaRead.model_validate(direccion) for direccion in direcciones]
            return lista_direcciones

    def actualizar_direccion_entrega(self, direccion_id: int, direccion_data: DireccionEntregaUpdate, usuario_id: int) -> DireccionEntregaRead:
        with UsuarioUnitOfWork(self._session) as uow:
            direccion = uow.direccion_entrega.get_by_id(direccion_id)
            if not direccion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")
            
            if direccion.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para acceder a esta funcionalidad"
                )

            hay_principal = uow.direccion_entrega.get_es_principal(direccion.usuario_id)
            if hay_principal and direccion_data.es_principal:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una direccion principal para este usuario")
            
            direccion_actualizada = direccion_data.model_dump(exclude_unset=True)
            for field, value in direccion_actualizada.items():
                setattr(direccion, field, value)

            uow.direccion_entrega.add(direccion)

            return DireccionEntregaRead.model_validate(direccion)
        
    def eliminar_direccion_entrega(self, direccion_id: int, usuario_id: int) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            direccion = uow.direccion_entrega.get_by_id(direccion_id)
            if not direccion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")
            
            if direccion.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No tienes los permisos para realizar esta accion"
                )
            direccion.activo = False
            direccion.deleted_at = datetime.now(timezone.utc)
            uow.direccion_entrega.add(direccion)
        
    def asignar_rol(self, admin_id: int, informacion: AdministrarRol) -> UsuarioRead:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = self._get_or_404(uow, informacion.usuario_id)
            rol = uow.rol.get_by_codigo(informacion.codigo_rol)
            if not rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
            if rol in usuario.roles:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya tiene asignado este rol")
            
            uow.usuario_rol.add(UsuarioRol(
                usuario_id = usuario.id,
                rol_codigo = informacion.codigo_rol,
                asignado_por_id = admin_id,
                expires_at = informacion.expires_at,
                created_at = datetime.now(timezone.utc)
            ))
            uow.refresh(usuario)
            usuario_rol_asignado = self._get_or_404(uow, usuario.id)
            return UsuarioRead.model_validate(usuario_rol_asignado)
        
    def quitar_rol(self, informacion: AdministrarRol) -> None:
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(informacion.usuario_id)
            rol = uow.rol.get_by_codigo(informacion.codigo_rol)
            usuario_rol = uow.usuario_rol.get_link(informacion.usuario_id, informacion.codigo_rol)
            if not usuario:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            if not rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
            if not usuario_rol:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no tiene asignado este rol")
            
            uow.usuario_rol.delete(usuario_rol)
            uow.refresh(usuario)
            usuario_rol_revocado = self._get_or_404(uow, usuario.id)
            return UsuarioRead.model_validate(usuario_rol_revocado)
        
    def desactivar_usuario(self, usuario_id: int):
        with UsuarioUnitOfWork(self._session) as uow:
            usuario = uow.usuario.get_by_id(usuario_id)
            if not usuario: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            if not usuario.activo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya se encuentra desactivado")
            usuario.deleted_at = datetime.now(timezone.utc)
            usuario.activo = False
            uow.usuario.add(usuario)
            
