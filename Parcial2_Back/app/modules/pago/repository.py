from sqlmodel import Session, select, func, delete
from app.core.repository import BaseRepository
from app.modules.pago.models import Pago

class PagoRepository(BaseRepository[Pago]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pago)