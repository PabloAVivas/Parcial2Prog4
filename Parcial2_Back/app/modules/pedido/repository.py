from sqlmodel import Session, select, func, delete
from app.core.repository import BaseRepository
from app.modules.pedido.models import Pedido

class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)