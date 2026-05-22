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

class DetallePedidoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, instance: DetallePedido) -> DetallePedido:
        self.session.add(instance)
        return instance

class HistorialEstadoPedidoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, instance: HistorialEstadoPedido) -> HistorialEstadoPedido:
        self.session.add(instance)
        return instance