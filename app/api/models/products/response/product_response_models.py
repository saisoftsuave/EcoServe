from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from app.core.base_response import BaseResponse







class ProductImageData(BaseModel):
    id: UUID
    product_id: UUID
    image: str
    primary_image: bool

    class Config:
        orm_mode = True
        from_attributes = True


class ReviewData(BaseModel):
    id: UUID
    product_id: UUID
    reviewer_id: UUID
    rating: int
    review_message: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True


class InventoryData(BaseModel):
    id: UUID
    product_id: UUID
    warehouse_id: UUID
    quantity: int

    class Config:
        orm_mode = True
        from_attributes = True


class CartData(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    quantity: int

    class Config:
        orm_mode = True
        from_attributes = True


class OrderItemData(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    unit_price: float

    class Config:
        orm_mode = True
        from_attributes = True


class PaymentData(BaseModel):
    id: UUID
    order_id: UUID
    amount: float
    status: str
    payment_method: str
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
        from_attributes = True


class WarehouseData(BaseModel):
    id: UUID
    name: str
    address: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True


class SessionData(BaseModel):
    id: UUID
    user_id: UUID
    session_token: str

    class Config:
        orm_mode = True
        from_attributes = True


class UserData(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    session: Optional[SessionData] = None
    reviews: List[ReviewData]
    cart: List[CartData]
    orders: List["OrderData"]

    class Config:
        orm_mode = True
        from_attributes = True


class OrderData(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime]
    address_id: str
    user: Optional[UserData] = None
    order_items: List[OrderItemData]
    payments: List[PaymentData]

    class Config:
        orm_mode = True
        from_attributes = True


class ProductData(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    price: float
    image: str
    category_id: int
    # category: Optional[CategoryData] = None
    images: List[ProductImageData]
    reviews: List[ReviewData]
    inventories: List[InventoryData]
    cart: List[CartData]
    order_items: List[OrderItemData]

    class Config:
        orm_mode = True
        from_attributes = True

class CategoryData(BaseModel):
    id: int
    name: str
    products: List[ProductData]

    class Config:
        orm_mode = True
        from_attributes = True


# ----------------------------------
# Response Schemas
# ----------------------------------

class CategoryResponse(BaseResponse[CategoryData]):
    pass

class ProductImageResponse(BaseResponse[ProductImageData]):
    pass

class ReviewResponse(BaseResponse[ReviewData]):
    pass

class InventoryResponse(BaseResponse[InventoryData]):
    pass

class CartResponse(BaseResponse[CartData]):
    pass

class OrderItemResponse(BaseResponse[OrderItemData]):
    pass

class PaymentResponse(BaseResponse[PaymentData]):
    pass

class WarehouseResponse(BaseResponse[WarehouseData]):
    pass

class SessionResponse(BaseResponse[SessionData]):
    pass

class UserResponse(BaseResponse[UserData]):
    pass

class OrderResponse(BaseResponse[OrderData]):
    pass

class ProductResponse(BaseResponse[ProductData]):
    pass
