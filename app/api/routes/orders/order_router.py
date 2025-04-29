from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.cart.db.cart import Cart
from app.api.models.orders.db.order import Order
from app.api.models.orders.db.order_item import OrderItem
from app.api.routes.user.user_service import get_current_user
from app.api.services.order_service import (
    create_order_service,
    get_order_service,
    get_order_item_service,
    update_order_item_service,
    delete_order_item_service
)
from app.core.db import get_db

order_router = APIRouter(prefix="/orders", tags=["Order Items"])

@order_router.post("", status_code=status.HTTP_201_CREATED)
async def create_order_route(
    order_item_data: List[Cart],
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        item = await create_order_service(session, order_item_data, user_id=user.id)
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@order_router.get("/{order_id}", response_model=Order)
async def read_order(
    order_id: str,
    session: AsyncSession = Depends(get_db)
):
    try:
        items = await get_order_service(session, order_id)
        if not items:
            raise HTTPException(status_code=404, detail="Order not found")
        return items
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@order_router.get("/{order_id}/items/{item_id}", response_model=OrderItem)
async def read_order_item(
    order_id: UUID,
    item_id: UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    item = await get_order_item_service(session, order_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return item

@order_router.put("/{order_id}/items/{item_id}", response_model=OrderItem)
async def update_order_item_route(
    order_id: UUID,
    item_id: UUID,
    order_item_data: Cart,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        item = await update_order_item_service(session, order_id, item_id, order_item_data)
        if not item:
            raise HTTPException(status_code=404, detail="OrderItem not found")
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@order_router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item_route(
    order_id: UUID,
    item_id: UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        success = await delete_order_item_service(session, order_id, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="OrderItem not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))