import uuid
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship

class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str
    description: Optional[str] = None
    price: float
    image: str
    category_id: int = Field(foreign_key="product_categories.id")

    category: Optional["ProductCategory"] = Relationship(back_populates="products", sa_relationship_kwargs={"lazy": "selectin"})
    images: List["ProductImage"] = Relationship(back_populates="product", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(back_populates="product", sa_relationship_kwargs={"lazy": "selectin"})
    inventories: List["Inventory"] = Relationship(back_populates="product", sa_relationship_kwargs={"lazy": "selectin"})
    cart: List["Cart"] = Relationship(back_populates="product", sa_relationship_kwargs={"lazy": "selectin"})
    order_items: List["OrderItem"] = Relationship(back_populates="product", sa_relationship_kwargs={"lazy": "selectin"})