from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.cart.db.cart import Cart
from app.api.models.orders.db.order import Order
from app.api.models.orders.db.order_item import OrderItem
from app.api.models.orders.order_request import OrderUpdate
from app.api.utils.order_status import OrderStatus


# Custom exceptions
class OrderServiceError(Exception):
    """Base exception for order service operations."""
    pass


class OrderNotFoundError(OrderServiceError):
    pass


class OrderItemNotFoundError(OrderServiceError):
    pass


class DuplicateOrderItemError(OrderServiceError):
    pass


async def create_order_service(db: AsyncSession, cart_data: List[Cart], user_id: str) -> Order:
    # Calculate total and create order
    total = sum(item.quantity * float(item.unit_price) for item in cart_data)
    db_order = Order(
        user_id=user_id,
        total_amount=total,
        status=OrderStatus.PENDING,
        address_id="",
        created_at=datetime.utcnow()
    )
    db.add(db_order)
    try:
        await db.commit()
        await db.refresh(db_order)
    except Exception:
        await db.rollback()
        raise OrderServiceError("Failed to create order")

    # Create order items
    order_items = []
    for item in cart_data:
        oi = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        order_items.append(oi)
    db.add_all(order_items)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise DuplicateOrderItemError("Duplicate order item detected")
    except Exception:
        await db.rollback()
        raise OrderServiceError("Failed to save order items")
    return db_order


async def get_order_service(db: AsyncSession, order_id: UUID) -> Order:
    order = await db.get(Order, order_id)
    if not order:
        raise OrderNotFoundError(f"Order id {order_id} not found")
    return order


async def get_orders_service(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
    stmt = select(Order).where(Order.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_order_item_service(db: AsyncSession, order_id: UUID, item_id: UUID) -> OrderItem:
    stmt = select(OrderItem).where(
        OrderItem.order_id == order_id,
        OrderItem.id == item_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise OrderItemNotFoundError(f"OrderItem id {item_id} not found in order {order_id}")
    return item


async def update_order_item_service(
        db: AsyncSession,
        order_id: UUID,
        item_id: UUID,
        order_item_data: Cart
) -> OrderItem:
    # Fetch item
    item = await get_order_item_service(db, order_id, item_id)
    # Update fields
    for key, value in order_item_data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    db.add(item)
    try:
        await db.commit()
        await db.refresh(item)
    except Exception:
        await db.rollback()
        raise OrderServiceError("Failed to update order item")
    return item


async def delete_order_item_service(db: AsyncSession, order_id: UUID, item_id: UUID) -> bool:
    # Fetch item
    try:
        item = await get_order_item_service(db, order_id, item_id)
    except OrderItemNotFoundError:
        return False
    try:
        await db.delete(item)
        await db.commit()
    except Exception:
        await db.rollback()
        raise OrderServiceError("Failed to delete order item")
    return True


async def update_order_service(db: AsyncSession, order_id: UUID, order_update: OrderUpdate) -> Order:
    order = await db.get(Order, order_id)
    if not order:
        raise OrderNotFoundError(f"Order id {order_id} not found")
    if order_update.status:
        order.status = order_update.status
        order.updated_at = datetime.utcnow()
    db.add(order)
    try:
        await db.commit()
        await db.refresh(order)
    except Exception:
        await db.rollback()
        raise OrderServiceError("Failed to update order")
    return order


async def delete_order_service(db: AsyncSession, order_id: UUID) -> bool:
    order = await db.get(Order, order_id)
    if not order:
        return False
    try:
        # Delete associated items first
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        items = (await db.execute(stmt)).scalars().all()
        for item in items:
            await db.delete(item)
        await db.delete(order)
        await db.commit()
    except Exception:
        await db.rollback()
        raise OrderServiceError("Failed to delete order")
    return True
