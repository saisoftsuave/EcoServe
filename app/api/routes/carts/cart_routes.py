from sqlite3 import IntegrityError
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette import status
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from app.api.models.cart.cart_request import AddToCart, UpdateCartQuantity
from app.api.models.cart.db.cart import Cart
from app.api.routes.user.user_service import get_current_user
from app.api.services.cart_service import (
    add_to_cart_service,
    remove_from_cart_service,
    increase_cart_product_quantity_service,
    get_cart_service
)
from app.core.db import get_db
from app.api.models.products.response.product_response_models import BaseResponse

logger = logging.getLogger(__name__)
cart_router = APIRouter(prefix="/cart", tags=["cart"])

def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)


@cart_router.post("/", response_model=BaseResponse[Cart], status_code=201)
async def add_to_cart(request: AddToCart, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        request.user_id = user.id
        result = await add_to_cart_service(db, request)
        return BaseResponse(data=result)
    except ValueError as e:
        logger.warning("Validation error adding to cart: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except IntegrityError as ie:
        logger.warning("Integrity error adding to cart: %s", ie)
        return error_response("Item already exists in cart", status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error adding to cart", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@cart_router.delete("/{cart_id}", response_model=BaseResponse[None], status_code=200)
async def delete_product(cart_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        if await remove_from_cart_service(db, cart_id) is None:
            return error_response("Cart item not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(message="Cart item deleted successfully")
    except ValueError as e:
        logger.warning("Value error deleting cart item %s: %s", cart_id, e)
        return error_response(str(e), status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        logger.error("Error deleting cart item %s", cart_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@cart_router.put("/{cart_id}", response_model=BaseResponse[Cart])
async def update_product(cart_id: str, cart_update: UpdateCartQuantity, db: AsyncSession = Depends(get_db),
                         user=Depends(get_current_user)):
    try:
        cart = await increase_cart_product_quantity_service(db, cart_update, cart_id)
        if cart is None:
            return error_response("Cart item not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=cart)
    except ValueError as e:
        logger.warning("Validation error updating cart item %s: %s", cart_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error updating cart item %s", cart_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@cart_router.get("/", response_model=BaseResponse[List[Cart]], status_code=200)
async def get_cart(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await get_cart_service(db, user.id)
        return BaseResponse(data=result)
    except Exception as ex:
        logger.error("Error getting cart for user %s", user.id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
