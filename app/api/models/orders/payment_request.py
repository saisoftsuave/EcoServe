from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.api.models.orders.db.payments import PaymentStatus


class PaymentCreate(BaseModel):
    order_id: UUID
    amount: float
    payment_method: str

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None