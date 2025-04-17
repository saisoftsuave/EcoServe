import uuid
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class ProductImage(SQLModel, table=True):
    __tablename__ = "product_images"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    product_id: uuid.UUID = Field(foreign_key="products.id")
    image: str
    primary_image: bool = Field(default=False)


    product: Optional["Product"] = Relationship(back_populates="images")