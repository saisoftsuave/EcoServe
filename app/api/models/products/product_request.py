from typing import Optional

from sqlmodel import SQLModel


class ProductCreate(SQLModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    image:str

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None