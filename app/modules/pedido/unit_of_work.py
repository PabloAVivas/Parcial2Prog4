from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.pedido.repository import PedidoRepository, DetallePedidoRepository, HistorialEstadoPedidoRepository
from app.modules.producto.repository import ProductoRepository
from app.modules.pago.repository import PagoRepository
from app.modules.ingrediente.repository import IngredienteRepository
from app.modules.usuarios.repository import UsuarioRepository, DireccionEntregaRepository

class PedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pedido = PedidoRepository(session)
        self.producto = ProductoRepository(session)
        self.pago = PagoRepository(session)
        self.ingrediente = IngredienteRepository(session)
        self.detalle_pedido = DetallePedidoRepository(session)
        self.historial_estado_pedido = HistorialEstadoPedidoRepository(session)
        self.usuario = UsuarioRepository(session)
        self.direccion_entrega = DireccionEntregaRepository(session)