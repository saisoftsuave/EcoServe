from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette import status
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

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
from app.api.models.products.response.product_response_models import BaseResponse

logger = logging.getLogger(__name__)
order_router = APIRouter(prefix="/orders", tags=["Order Items"])

def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)

@order_router.post("", response_model=BaseResponse[Order], status_code=status.HTTP_201_CREATED)
async def create_order_route(
    order_item_data: List[Cart],
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        item = await create_order_service(session, order_item_data, user_id=user.id)
        return BaseResponse(data=item)
    except ValueError as e:
        logger.warning("Validation error creating order: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error creating order", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@order_router.get("/{order_id}", response_model=BaseResponse[Order])
async def read_order(
    order_id: str,
    session: AsyncSession = Depends(get_db)
):
    try:
        items = await get_order_service(session, order_id)
        if not items:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=items)
    except Exception as ex:
        logger.error("Error reading order %s", order_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@order_router.get("/{order_id}/items/{item_id}", response_model=BaseResponse[OrderItem])
async def read_order_item(
    order_id: UUID,
    item_id: UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        item = await get_order_item_service(session, order_id, item_id)
        if not item:
            return error_response("OrderItem not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=item)
    except Exception as ex:
        logger.error("Error fetching order item %s in order %s", item_id, order_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@order_router.put("/{order_id}/items/{item_id}", response_model=BaseResponse[OrderItem])
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
            return error_response("OrderItem not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=item)
    except ValueError as e:
        logger.warning("Validation error updating order item %s: %s", item_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Error updating order item %s", item_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@order_router.delete("/{order_id}/items/{item_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
async def delete_order_item_route(
    order_id: UUID,
    item_id: UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        success = await delete_order_item_service(session, order_id, item_id)
        if not success:
            return error_response("OrderItem not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(message="OrderItem deleted successfully")
    except Exception as ex:
        logger.error("Error deleting order item %s", item_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
