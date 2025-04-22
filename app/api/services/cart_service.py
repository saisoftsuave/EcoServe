from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.cart.cart_request import AddToCart, UpdateCartQuantity
from app.api.models.cart.db.cart import Cart
from app.api.models.products import Product
from app.api.models.user.db import User
from app.core.errors import UserNotFound


async def add_to_cart_service(db: AsyncSession, cart_item: AddToCart) -> Cart:
    if not await db.get(Product, cart_item.product_id):
        raise ValueError("Product not found")
    cart_model = Cart(**cart_item.dict())
    db.add(cart_model)
    await db.commit()
    await db.refresh(cart_model)
    return cart_model


async def remove_from_cart_service(db: AsyncSession, id: str) -> Cart:
    cart_item = await db.get(Cart, id)
    if not cart_item:
        raise ValueError("Cart Item not found")
    await db.delete(cart_item)
    await db.commit()
    return cart_item


async def increase_cart_product_quantity_service(db: AsyncSession, quantity: UpdateCartQuantity, cart_id: str) -> Cart:
    cart_item = await db.get(Cart, cart_id)
    if not cart_item:
        raise ValueError("Cart Item not found")
    cart_item.quantity = quantity.quantity
    await db.commit()
    await db.refresh(cart_item)
    return cart_item


async def get_cart_service(db: AsyncSession, user_id: str) -> List[Product]:
    db_user = await db.get(User,user_id)
    if not db_user:
        raise UserNotFound()
    products = [cart_item.product for cart_item in db_user.cart]
    return products
