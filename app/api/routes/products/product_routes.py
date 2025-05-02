from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette import status
from typing import List
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from starlette.responses import JSONResponse

from app.api.models.products.db.product import Product
from app.api.models.products.product_request import ProductCreate, ProductUpdate
from app.api.models.products.response.product_response_models import (
    BaseResponse, ProductResponse, ProductData
)
from app.api.services.product_service import (
    create_product_service,
    get_product_service,
    get_products_service,
    update_product_service,
    delete_product_service,
    get_products_by_name_service
)
from app.api.routes.user.user_service import get_current_user
from app.core.base_response import BaseResponse
from app.core.db import get_db

logger = logging.getLogger(__name__)
product_router = APIRouter(prefix="/products", tags=["Products"])

"""
Note: Will add roles like merchant and customer
"""

def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)


@product_router.post("/", response_model=BaseResponse[List[ProductData]], status_code=201)
async def create_product(
    products: List[ProductCreate],
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> BaseResponse | JSONResponse:
    try:
        created = []
        for item in products:
            p = await create_product_service(db, item)
            created.append(p)
        data = [ProductData.model_validate(p) for p in created]
        return BaseResponse(data=data)
    except ValueError as e:
        logger.warning("Validation error creating products: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except IntegrityError as ie:
        logger.warning("Integrity error creating product: %s", ie)
        return error_response("Product with this name already exists", status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error creating products", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@product_router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    try:
        product = await get_product_service(db, product_id)
        if not product:
            return ProductResponse(status="error", message="Product not found")
        return ProductResponse(data=ProductData.model_validate(product))
    except Exception as ex:
        logger.error("Error reading product %s", product_id, exc_info=ex)
        return ProductResponse(status="error", message="Internal server error")

"""
Note: for performance only returning the primary image and minimal details
"""


@product_router.get("/", response_model=BaseResponse[List[ProductData]])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse | JSONResponse:
    try:
        products = await get_products_service(db, skip=skip, limit=limit)
        data = [ProductData.model_validate(p) for p in products]
        return BaseResponse(data=data)
    except Exception as ex:
        logger.error("Error reading products list", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@product_router.get("/name/", response_model=BaseResponse[List[ProductData]])
async def read_products_by_name(
    name: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse | JSONResponse:
    try:
        products = await get_products_by_name_service(db, skip=skip, limit=limit, name_filter=name)
        data = [ProductData.model_validate(p) for p in products]
        return BaseResponse(data=data)
    except Exception as ex:
        logger.error("Error searching products by name '%s'", name, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@product_router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> ProductResponse:
    try:
        product = await update_product_service(db, product_id, product_update)
        if not product:
            return ProductResponse(status="error", message="Product not found")
        return ProductResponse(data=ProductData.model_validate(product))
    except ValueError as e:
        logger.warning("Validation error updating product %s: %s", product_id, e)
        return ProductResponse(status="error", message=str(e))
    except IntegrityError as ie:
        logger.warning("Integrity error updating product %s: %s", product_id, ie)
        return ProductResponse(status="error", message="Product with this name already exists")
    except Exception as ex:
        logger.error("Unexpected error updating product %s", product_id, exc_info=ex)
        return ProductResponse(status="error", message="Internal server error")


@product_router.delete("/{product_id}", response_model=BaseResponse[None], status_code=200)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> JSONResponse | BaseResponse:
    try:
        deleted = await delete_product_service(db, product_id)
        if not deleted:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=None, message="Product deleted successfully")
    except Exception as ex:
        logger.error("Error deleting product %s", product_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
