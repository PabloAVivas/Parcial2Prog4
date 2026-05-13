from sqlmodel import Session, select, func
from app.core.repository import BaseRepository
from app.modules.categoria.models import Categoria

class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Categoria)

    def get_activo(self, offset: int = 0, limit: int = 100, nombre: str = None) -> list[Categoria]:
        query = select(Categoria).where(Categoria.activo == True)
        if nombre:
            query = query.where(Categoria.nombre.ilike(f"%{nombre}%"))
        query = query.order_by(Categoria.id)
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )

    def count(self) -> int:
        query = select(func.count()).select_from(Categoria).where(Categoria.activo == True)
        return self.session.exec(query).one()
    
    def count_activo(self, nombre: str = None) -> int:
        query = select(func.count()).select_from(Categoria).where(Categoria.activo == True)
        if nombre:
            query = query.where(Categoria.nombre.ilike(f"%{nombre}%"))
        
        return self.session.exec(query).one()