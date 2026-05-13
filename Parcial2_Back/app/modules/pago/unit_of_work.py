from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.producto.repository import ProductoRepository
from app.modules.categoria.repository import CategoriaRepository
from app.modules.ingrediente.repository import IngredienteRepository

class ProductoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.producto = ProductoRepository(session)
        self.categoria = CategoriaRepository(session)
        self.ingrediente = IngredienteRepository(session)