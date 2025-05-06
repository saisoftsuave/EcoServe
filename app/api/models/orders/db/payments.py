from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    id: UUID = Field(primary_key=True)
    order_id: UUID = Field(foreign_key="order.id")
    amount: float
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: str
    transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    # Id generated from strip payment gateway
    # stripe_id:str

    order: Optional["Order"] = Relationship(back_populates="payments", sa_relationship_kwargs={"lazy": "selectin"})
