import uuid
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

class Inventory(SQLModel, table=True):
    __tablename__ = "inventories"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    product_id: uuid.UUID = Field(foreign_key="products.id")
    warehouse_id: uuid.UUID = Field(foreign_key="warehouses.id")
    quantity: int


    product: Optional["Product"] = Relationship(back_populates="inventories",sa_relationship_kwargs={"lazy": "selectin"})
    warehouse: Optional["Warehouse"] = Relationship(back_populates="inventories",sa_relationship_kwargs={"lazy": "selectin"})