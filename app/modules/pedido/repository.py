from sqlmodel import Session, select, func, delete
from app.core.repository import BaseRepository
from sqlalchemy.orm import selectinload
from app.modules.pedido.models import Pedido, HistorialEstadoPedido, DetallePedido, FormaPago, EstadoPedido


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    def get_activo(self, offset: int = 0, limit: int = 100) -> list[Pedido]:
        query = select(Pedido).where(Pedido.activo == True)
        
        query = query.options(
            selectinload(Pedido.detalle_pedidos),
            selectinload(Pedido.historial_estado),
            selectinload(Pedido.usuario),
            selectinload(Pedido.direccion)
        )
            
        query = query.order_by(Pedido.id)
        
        return list(
            self.session.exec(query.offset(offset).limit(limit)).all()
        )
    
    def get_by_id_pedido(self, pedido_id: int) -> Pedido:
        query = select(Pedido).where(Pedido.id == pedido_id).options(
            selectinload(Pedido.detalle_pedidos),
            selectinload(Pedido.historial_estado),
            selectinload(Pedido.usuario),
            selectinload(Pedido.direccion)
        )
        return self.session.exec(query).first()

    def get_estado(self, codigo:str) -> EstadoPedido:
        return self.session.get(EstadoPedido, codigo.upper())
    
    def get_forma(self, codigo:str) -> FormaPago:
        return self.session.get(FormaPago, codigo.upper())
    
    def get_pedidos_by_usuario_id(self, usuario_id: int) -> list[Pedido]:
        query = select(Pedido).where(Pedido.usuario_id == usuario_id)
        query = query.options(
            selectinload(Pedido.detalle_pedidos),
            selectinload(Pedido.historial_estado),
            selectinload(Pedido.usuario),
            selectinload(Pedido.direccion)
        )
        query = query.order_by(Pedido.id)
        return self.session.exec(query).all()

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