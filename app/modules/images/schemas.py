from typing import Optional
from sqlmodel import SQLModel
from datetime import datetime

class ImagenPublic(SQLModel):
    id: int
    public_id: str
    url: str
    filename: str
    format: str
    width: int
    height: int
    bytes: int
    created_at: datetime