from sqlmodel import Session, select, func, delete
from app.core.repository import BaseRepository
from app.modules.producto.models import Producto, ProductoCategoriaLink, ProductoIngredienteLink

class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    def get_activo(self, offset: int = 0, limit: int = 100, nombre: str = None) -> list[Producto]:
        query = select(Producto).where(Producto.activo == True)
        if nombre:
            query = query.where(Producto.nombre.ilike(f"%{nombre}%"))
            
        query = query.order_by(Producto.id)
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )
    
    def add_categoria(self, producto_id: int, categoria_id: int, es_principal: bool = False) -> ProductoCategoriaLink:
        link = ProductoCategoriaLink(
            producto_id=producto_id,
            categoria_id=categoria_id,
            es_principal=es_principal,
        )
        self.session.add(link)
        self.session.flush()
        return link

    def add_ingrediente(self, producto_id: int, ingrediente_id: int, es_removible: bool = False) -> ProductoIngredienteLink:
        link = ProductoIngredienteLink(
            producto_id=producto_id,
            ingrediente_id=ingrediente_id,
            es_removible=es_removible,
        )
        self.session.add(link)
        self.session.flush()
        return link
    
    def eliminar_categoria(self, producto_id:int) -> None:
        statement = delete(ProductoCategoriaLink).where(ProductoCategoriaLink.producto_id == producto_id)
        self.session.exec(statement)
        self.session.flush()

    def eliminar_ingrediente(self, producto_id:int) -> None:
        statement = delete(ProductoIngredienteLink).where(ProductoIngredienteLink.producto_id == producto_id)
        self.session.exec(statement)
        self.session.flush()

    def count(self) -> int:
        query = select(func.count()).select_from(Producto).where(Producto.activo == True)
        return self.session.exec(query).one
    
    def count_activo(self, nombre: str = None) -> int:
        query = select(func.count()).select_from(Producto).where(Producto.activo == True)
        if nombre:
            query = query.where(Producto.nombre.ilike(f"%{nombre}%"))
        
        return self.session.exec(query).one()
