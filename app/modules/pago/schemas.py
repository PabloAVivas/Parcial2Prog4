from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

class PagoCreate(SQLModel):
    pedido_id: int
    mp_payment_id: int
    mp_status: str
    mp_status_detail: str
    external_reference: str
    idempotency_key: str
    transaction_amount: float
    payment_method_id: str

class PagoRead(SQLModel):
    pedido_id: int
    mp_payment_id: int
    mp_status: str
    mp_status_detail: str
    external_reference: str
    idempotency_key: str
    transaction_amount: float
    payment_method_id: str
    created_at: datetime
    updated_at: datetime

class PagoUpdate(SQLModel):
    pedido_id: int
    mp_payment_id: int
    mp_status: str
    mp_status_detail: str
    external_reference: str
    idempotency_key: str
    transaction_amount: float
    payment_method_id: str