from app.core.repository import BaseRepository
from app.modules.usuarios.model import Usuario
from sqlmodel import Session, select, func, delete

class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)

    def get_usuarios(self, offset: int = 0, limit: int = 100) -> list[Usuario]:
        query = select(Usuario)

        query = query.order_by(Usuario.id)
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )