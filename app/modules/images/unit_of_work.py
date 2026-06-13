from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.images.repository import ImagenRepository

class ImagenUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.imagen = ImagenRepository(session)