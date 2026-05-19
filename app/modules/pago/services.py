from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.pago.models import Pago
from app.modules.pago.schemas import PagoCreate, PagoRead, PagoUpdate
from app.modules.pago.unit_of_work import PagoUnitOfWork
from datetime import datetime, timezone

class PagoService:
    def __init__(self, session: Session) -> None:
        self._session = session