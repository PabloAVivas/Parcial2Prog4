from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.images.model import Imagen

class ImagenRepository(BaseRepository[Imagen]):

    def __init__(self, session: Session):
        super().__init__(session, Imagen)

    def get_all_ordered(self) -> list[Imagen]:
        return list(
            self.session.exec(
                select(Imagen).order_by(Imagen.created_at.desc())
            ).all()
        )
    
    def get_by_public_id(self, public_id: str) -> Imagen | None:
        return self.session.exec(
            select(Imagen).where(Imagen.public_id == public_id)
        ).first()