from typing import Optional

from sqlmodel import SQLModel


class AddToCart(SQLModel):
    user_id: Optional[str] = ""
    product_id: str
    quantity: int

class RemoveFromCart(SQLModel):
    cart_id: str


class UpdateCartQuantity(SQLModel):
    quantity: int
