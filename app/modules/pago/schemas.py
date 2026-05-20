from sqlmodel import SQLModel
from datetime import datetime

class PagoCreate(SQLModel):
    pedido_id: int
    transaction_amount: float

class PagoRead(SQLModel):
    id: int
    pedido_id: int
    transaction_amount: float
    created_at: datetime