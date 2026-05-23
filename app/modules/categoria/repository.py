from sqlmodel import Session, select, func, text
from app.core.repository import BaseRepository
from sqlalchemy.orm import selectinload
from app.modules.categoria.models import Categoria
from app.modules.producto.models import ProductoCategoriaLink

class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Categoria)

    def get_activo(self, offset: int = 0, limit: int = 100, nombre: str = None) -> list[Categoria]:
        query = select(Categoria).where(Categoria.activo == True)

        query = query.options(
            selectinload(Categoria.productos),
            selectinload(Categoria.padre)
        )

        if nombre:
            query = query.where(Categoria.nombre.ilike(f"%{nombre}%"))
        query = query.order_by(Categoria.id)
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )

    def get_by_id_productos(self, categoria_id: int) -> Categoria:
        query = select(Categoria).where(Categoria.id == categoria_id).options(
            selectinload(Categoria.productos),
            selectinload(Categoria.padre)
        )
        return self.session.exec(query).first()

    def count(self) -> int:
        query = select(func.count()).select_from(Categoria).where(Categoria.activo == True)
        return self.session.exec(query).one()
    
    def count_activo(self, nombre: str = None) -> int:
        query = select(func.count()).select_from(Categoria).where(Categoria.activo == True)
        if nombre:
            query = query.where(Categoria.nombre.ilike(f"%{nombre}%"))
        
        return self.session.exec(query).one()
    
    def get_tree(self) ->list [dict]:
        result = self.session.exec(
            text(
                """
                WITH RECURSIVE tree AS (
                    SELECT id, parent_id, nombre, descripcion, imagen_url, 0 AS depth
                    FROM categoria
                    WHERE parent_id IS NULL AND activo = true

                    UNION ALL

                    SELECT c.id, c.parent_id, c.nombre, c.descripcion, c.imagen_url, t.depth + 1
                    FROM categoria c
                    JOIN tree t ON c.parent_id = t.id
                    WHERE c.activo = true
                )
                SELECT * FROM tree ORDER BY depth, nombre;
                """
            )
        ).all()
        return [dict(row._mapping) for row in result]