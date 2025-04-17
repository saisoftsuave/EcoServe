import uuid
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship



class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    product_id: uuid.UUID = Field(foreign_key="products.id")
    reviewer_id: uuid.UUID = Field(foreign_key="User.id")
    rating: int
    review_message: Optional[str] = None


    product: Optional["Product"] = Relationship(back_populates="reviews")
    reviewer: Optional["User"] = Relationship(back_populates="reviews")