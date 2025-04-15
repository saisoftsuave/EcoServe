from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class ProductCategory(SQLModel, table=True):
    __tablename__ = "product_categories"
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={'autoincrement': True})
    name: str

    products: List["Product"] = Relationship(back_populates="category")
