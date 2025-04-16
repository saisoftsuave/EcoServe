import uuid
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str
    description: Optional[str] = None
    price: float
    category_id: int = Field(foreign_key="product_categories.id")


    category: Optional["ProductCategory"] = Relationship(back_populates="products")
    images: List["ProductImage"] = Relationship(back_populates="product")
    reviews: List["Review"] = Relationship(back_populates="product")
    inventories: List["Inventory"] = Relationship(back_populates="product")

