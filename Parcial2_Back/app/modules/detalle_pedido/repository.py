from sqlmodel import Session, select, func, delete
from app.core.repository import BaseRepository
from app.modules.detalle_pedido.models import DetallePedido

class DetallePedidoRepository(BaseRepository[DetallePedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DetallePedido)