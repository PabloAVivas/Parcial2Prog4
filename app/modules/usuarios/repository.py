from turtle import update

from app.core.repository import BaseRepository
from app.modules.usuarios.model import Usuario, Rol, RefreshToken, UsuarioRol, DireccionEntrega
from sqlmodel import Session, select, func, delete, udpate

class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)

    def get_by_email(self, email: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.email == email)
        return self.session.exec(statement).first()
    
    def desactivate_usuario(self, usuario_id: int) -> None:
        statement = update(Usuario).where(Usuario.id == usuario_id).values(activo=False)
        return self.session.exec(statement)
    
class RolRepository(BaseRepository[Rol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Rol)

    def get_by_codigo(self, codigo: str) -> Rol | None:
        statement = select(Rol).where(Rol.codigo == codigo.upper())
        return self.session.exec(statement).first()

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RefreshToken)

class UsuarioRolRepository(BaseRepository[UsuarioRol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, UsuarioRol)

    def get_link(self, usuario_id: int, rol_codigo: str) -> UsuarioRol | None:
        statement = select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id, UsuarioRol.rol_codigo == rol_codigo)
        return self.session.exec(statement).first()

class DireccionEntregaRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DireccionEntrega)

    def get_direcciones_by_usuario_id(self, usuario_id: int) -> list[DireccionEntrega]:
        statement = select(DireccionEntrega).where(DireccionEntrega.usuario_id == usuario_id)
        return self.session.exec(statement).all()

    def get_es_principal(self, usuario_id: int) -> DireccionEntrega | None:
        statement = select(DireccionEntrega).where(DireccionEntrega.usuario_id == usuario_id, DireccionEntrega.es_principal == True)
        return self.session.exec(statement).first()
    
    def delete(self, direccion_id: int) -> None:
        statement = delete(DireccionEntrega).where(DireccionEntrega.id == direccion_id)
        return self.session.exec(statement)
