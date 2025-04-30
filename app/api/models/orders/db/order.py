import uuid
from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
from app.api.utils.order_status import OrderStatus

class Order(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    user_id: uuid.UUID = Field(foreign_key="User.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    address_id: str

    user: Optional["User"] = Relationship(back_populates="orders", sa_relationship_kwargs={"lazy": "selectin"})
    order_items: List["OrderItem"] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "selectin"})
    payments: List["Payment"] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "selectin"})
