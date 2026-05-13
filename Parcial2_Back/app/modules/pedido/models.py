from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

class Pedido(SQLModel, table=True):
    __tablename__ = "pedido"

    id:Optional[int] = Field(default=None, primary_key=True)
    estado_codigo: str