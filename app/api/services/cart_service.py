from typing import List
from sqlmodel import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.cart.cart_request import AddToCart, UpdateCartQuantity
from app.api.models.cart.db.cart import Cart
from app.api.models.products import Product
from app.api.models.user.db import User
from app.core.errors import UserNotFound


class CartError(Exception):
    """Base exception for cart service errors."""
    pass


class ProductNotFoundError(CartError):
    pass


class CartItemNotFoundError(CartError):
    pass


class DuplicateCartItemError(CartError):
    pass


async def add_to_cart_service(db: AsyncSession, cart_item: AddToCart) -> Cart:
    # Ensure product exists
    product = await db.get(Product, cart_item.product_id)
    if not product:
        raise ProductNotFoundError("Product not found")
    # Create cart entry
    cart_model = Cart(**cart_item.dict())
    db.add(cart_model)
    try:
        await db.commit()
        await db.refresh(cart_model)
    except IntegrityError:
        await db.rollback()
        raise DuplicateCartItemError("Item already exists in cart")
    except Exception:
        await db.rollback()
        raise CartError("Failed to add item to cart")
    return cart_model


async def remove_from_cart_service(db: AsyncSession, cart_id: str) -> Cart:
    cart_item = await db.get(Cart, cart_id)
    if not cart_item:
        raise CartItemNotFoundError("Cart item not found")
    try:
        await db.delete(cart_item)
        await db.commit()
    except Exception:
        await db.rollback()
        raise CartError("Failed to remove cart item")
    return cart_item


async def increase_cart_product_quantity_service(
    db: AsyncSession,
    quantity_update: UpdateCartQuantity,
    cart_id: str
) -> Cart:
    cart_item = await db.get(Cart, cart_id)
    if not cart_item:
        raise CartItemNotFoundError("Cart item not found")
    cart_item.quantity = quantity_update.quantity
    try:
        await db.commit()
        await db.refresh(cart_item)
    except Exception:
        await db.rollback()
        raise CartError("Failed to update cart item quantity")
    return cart_item


async def get_cart_service(db: AsyncSession, user_id: str) -> List[Cart]:
    # Ensure user exists
    user = await db.get(User, user_id)
    if not user:
        raise UserNotFound(f"User with id {user_id} not found")
    try:
        statement = select(Cart).where(Cart.user_id == user_id)
        result = await db.execute(statement)
        items = result.scalars().all()
    except Exception:
        raise CartError("Failed to retrieve cart items")
    return items
