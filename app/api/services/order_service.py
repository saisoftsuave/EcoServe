from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.cart.db.cart import Cart
from app.api.models.orders.db.order import Order
from app.api.models.orders.db.order_item import OrderItem
from app.api.models.orders.order_request import OrderUpdate
from app.api.utils.order_status import OrderStatus

async def create_order_service(db: AsyncSession, cart_data: List[Cart], user_id: str) -> Order:
    db_order = Order(
        user_id=user_id,
        total_amount=sum(item.quantity * 10 for item in cart_data),  # Assuming unit_price=10 as in original
        status=OrderStatus.PENDING,
        address_id=""
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    order_items = [
        OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=10
        ) for item in cart_data
    ]

    db.add_all(order_items)
    await db.commit()

    return db_order

async def get_order_service(db: AsyncSession, order_id: str) -> Optional[Order]:
    result = await db.get(Order, order_id)
    return result

async def get_orders_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Order]:
    statement = select(Order).offset(skip).limit(limit)
    result = await db.exec(statement)
    return result.all()

async def get_order_item_service(db: AsyncSession, order_id: UUID, item_id: UUID) -> Optional[OrderItem]:
    statement = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.id == item_id)
    result = await db.exec(statement)
    return result.first()

async def update_order_item_service(
    db: AsyncSession,
    order_id: UUID,
    item_id: UUID,
    order_item_data: Cart
) -> Optional[OrderItem]:
    statement = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.id == item_id)
    result = await db.exec(statement)
    db_item = result.first()
    if db_item:
        update_data = order_item_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
    return db_item

async def delete_order_item_service(db: AsyncSession, order_id: UUID, item_id: UUID) -> bool:
    statement = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.id == item_id)
    result = await db.exec(statement)
    db_item = result.first()
    if db_item:
        await db.delete(db_item)
        await db.commit()
        return True
    return False

async def update_order_service(db: AsyncSession, order_id: UUID, order_update: OrderUpdate) -> Optional[Order]:
    db_order = await db.get(Order, order_id)
    if db_order:
        if order_update.status:
            db_order.status = order_update.status
            db_order.updated_at = datetime.utcnow()
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)
    return db_order

async def delete_order_service(db: AsyncSession, order_id: UUID) -> bool:
    order = await db.get(Order, order_id)
    if order:
        statement = select(OrderItem).where(OrderItem.order_id == order_id)
        order_items = await db.exec(statement)
        for item in order_items:
            await db.delete(item)
        await db.delete(order)
        await db.commit()
        return True
    return False