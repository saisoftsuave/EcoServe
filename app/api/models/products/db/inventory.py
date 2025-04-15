import uuid
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

class Inventory(SQLModel, table=True):
    __tablename__ = "inventories"
    id: uuid.UUID = Field(primary_key=True, default=uuid.uuid4())
    product_id: uuid.UUID = Field(foreign_key="products.id")
    warehouse_id: uuid.UUID = Field(foreign_key="warehouses.id")
    quantity: int


    product: Optional["Product"] = Relationship(back_populates="inventories")
    warehouse: Optional["Warehouse"] = Relationship(back_populates="inventories")