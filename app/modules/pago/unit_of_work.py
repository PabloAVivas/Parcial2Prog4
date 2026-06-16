from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.pago.repository import PagoRepository
from app.modules.pedido.repository import PedidoRepository, HistorialEstadoPedidoRepository, DetallePedidoRepository
from app.modules.ingrediente.repository import IngredienteRepository
from app.modules.producto.repository import ProductoRepository

class PagoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pago = PagoRepository(session)
        self.pedido = PedidoRepository(session)
        self.historial_estado_pedido = HistorialEstadoPedidoRepository(session)
        self.producto = ProductoRepository(session)
        self.ingrediente = IngredienteRepository(session)
        self.detalle_pedido = DetallePedidoRepository(session)