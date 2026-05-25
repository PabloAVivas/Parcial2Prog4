from datetime import timedelta, timezone, datetime
from sqlmodel import Session
from fastapi import HTTPException, status
from app.core.security import generar_refresh_token, hashear_password, verificar_password, create_access_token, calcular_hash_token
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.usuarios.models import Usuario, RefreshToken, Rol
from app.modules.usuarios.schemas import UsuarioRead
from app.modules.auth.schemas import UsuarioRegister, UsuarioLogin, Token


class AuthService:
    def __init__(self, session: Session):
        self._session = session

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
