import uuid
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouses"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str
    address: Optional[str] = None


    inventories: List["Inventory"] = Relationship(back_populates="warehouse",sa_relationship_kwargs={"lazy": "selectin"})