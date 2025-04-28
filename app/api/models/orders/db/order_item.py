import uuid
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

class OrderItem(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    order_id: uuid.UUID = Field(foreign_key="order.id")
    product_id: uuid.UUID = Field(foreign_key="products.id")
    quantity: int
    unit_price: float

    product: Optional["Product"] = Relationship(back_populates="order_items", sa_relationship_kwargs={"lazy": "selectin"})
    order: Optional["Order"] = Relationship(back_populates="order_items", sa_relationship_kwargs={"lazy": "selectin"})