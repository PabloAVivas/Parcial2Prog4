from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.detalle_pedido.repository import DetallePedidoRepository
from app.modules.producto.repository import ProductoRepository
from app.modules.pedido.repository import PedidoRepository
from app.modules.ingrediente.repository import IngredienteRepository

class DetallePedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.detalle_pedido = DetallePedidoRepository(session)
        self.producto = ProductoRepository(session)
        self.pedido = PedidoRepository(session)