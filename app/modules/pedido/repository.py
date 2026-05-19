from sqlmodel import Session, select, func, delete
from app.core.repository import BaseRepository
from app.modules.pedido.models import Pedido, HistorialEstadoPedido, DetallePedido, FormaPago, EstadoPedido

class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    def get_estado(self, codigo:str) -> EstadoPedido:
        return self.session.get(EstadoPedido, codigo.upper())
    
    def get_forma(self, codigo:str) -> FormaPago:
        return self.session.get(FormaPago, codigo.upper())
