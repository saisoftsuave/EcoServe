from typing import Optional

from sqlmodel import SQLModel


class CategoryCreate(SQLModel):
    name: str


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
