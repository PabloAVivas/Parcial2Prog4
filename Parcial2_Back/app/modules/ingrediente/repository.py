from sqlmodel import Session, select, func
from app.core.repository import BaseRepository
from app.modules.ingrediente.models import Ingrediente

class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)

    def get_activo(self, offset: int = 0, limit: int = 100, nombre: str = None) -> list[Ingrediente]:
        query = select(Ingrediente).where(Ingrediente.activo == True)
        if nombre:
            query = query.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
        query = query.order_by(Ingrediente.id)
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )

    def count(self) -> int:
        query = select(func.count()).select_from(Ingrediente).where(Ingrediente.activo == True)
        return self.session.exec(query).one()
    
    def count_activo(self, nombre: str = None) -> int:
        query = select(func.count()).select_from(Ingrediente).where(Ingrediente.activo == True)
        if nombre:
            query = query.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
        
        return self.session.exec(query).one()