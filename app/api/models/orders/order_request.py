from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.api.models.cart.db.cart import Cart
from app.api.utils.order_status import OrderStatus


class OrderCreate(BaseModel):
    user_id: int
    items: List[Cart]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemResponse]