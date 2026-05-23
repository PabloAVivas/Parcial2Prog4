from sqlmodel import Session, select, func
from app.core.repository import BaseRepository
from app.modules.ingrediente.models import Ingrediente
from sqlalchemy.orm import selectinload
from app.modules.producto.models import  ProductoIngredienteLink



class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)

    def get_activo(self, offset: int = 0, limit: int = 100, nombre: str = None) -> list[Ingrediente]:
        query = select(Ingrediente).where(Ingrediente.activo == True)

        query = query.options(
            selectinload(Ingrediente.producto_links)
        )

        if nombre:
            query = query.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
        query = query.order_by(Ingrediente.id)
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )
    
    def get_by_id_productos(self, ingrediente_id: int) -> Ingrediente:
        query = select(Ingrediente).where(Ingrediente.id == ingrediente_id).options(
            selectinload(Ingrediente.producto_links)
        )
        return self.session.exec(query).first()

    def count(self) -> int:
        query = select(func.count()).select_from(Ingrediente).where(Ingrediente.activo == True)
        return self.session.exec(query).one()
    
    def count_activo(self, nombre: str = None) -> int:
        query = select(func.count()).select_from(Ingrediente).where(Ingrediente.activo == True)
        if nombre:
            query = query.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
        
        return self.session.exec(query).one()