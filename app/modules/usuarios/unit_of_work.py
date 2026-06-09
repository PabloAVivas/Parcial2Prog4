from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.usuarios.repository import UsuarioRepository, RolRepository,  UsuarioRolRepository, DireccionEntregaRepository

class UsuarioUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.usuario = UsuarioRepository(session)
        self.rol = RolRepository(session)
        self.usuario_rol = UsuarioRolRepository(session)
        self.direccion_entrega = DireccionEntregaRepository(session)