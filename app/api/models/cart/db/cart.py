import uuid
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Cart(SQLModel, table=True):
    id: uuid.UUID = Field(default=uuid.uuid4(), primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="User.id")
    product_id: uuid.UUID = Field(foreign_key="products.id")
    quantity: int
    unit_price: Optional[float]

    product: Optional["Product"] = Relationship(back_populates="cart", sa_relationship_kwargs={"lazy": "selectin"})
    user: Optional["User"] = Relationship(back_populates="cart", sa_relationship_kwargs={"lazy": "selectin"})

# from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Numeric, func
# from sqlalchemy.orm import relationship, declarative_base
#
# Base = declarative_base()
#
# class Cart(Base):
#     __tablename__ = 'carts'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(String, nullable=False, index=True)
#     status = Column(String, default='open', nullable=False)  # open, saved, merged, etc.
#     created_at = Column(DateTime, server_default=func.now(), nullable=False)
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
#
#     # Relationships
#     items = relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')
#     coupons = relationship('Coupon', secondary='cart_coupons', back_populates='carts')
#
# class CartItem(Base):
#     __tablename__ = 'cart_items'
#     id = Column(Integer, primary_key=True)
#     cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False, index=True)
#     product_id = Column(String, nullable=False)
#     quantity = Column(Integer, nullable=False, default=1)
#     price = Column(Numeric(10,2), nullable=False)  # unit price at time of addition
#
#     cart = relationship('Cart', back_populates='items')
#
# class Coupon(Base):
#     __tablename__ = 'coupons'
#     code = Column(String, primary_key=True)
#     description = Column(String)
#     discount_type = Column(String, nullable=False)  # 'amount' or 'percentage'
#     discount_value = Column(Numeric(10,2), nullable=False)
#     expires_at = Column(DateTime)
#
#     carts = relationship('Cart', secondary='cart_coupons', back_populates='coupons')
#
# class CartCoupon(Base):
#     __tablename__ = 'cart_coupons'
#     cart_id = Column(Integer, ForeignKey('carts.id'), primary_key=True)
#     coupon_code = Column(String, ForeignKey('coupons.code'), primary_key=True)
#     applied_at = Column(DateTime, server_default=func.now(), nullable=False)
