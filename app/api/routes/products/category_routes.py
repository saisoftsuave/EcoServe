from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select
from starlette import status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from app.api.models.products import ProductCategory, Product
from app.api.models.products.category_request import CategoryCreate, CategoryUpdate
from app.api.models.products.product_request import ProductCreate
from app.api.services.category_service import (
    create_category_service,
    delete_category_service,
    update_category_service,
    add_product_to_category_service,
    remove_product_from_category_service, get_categories_service
)
from app.api.routes.user.user_service import get_current_user
from app.core.db import get_db
from app.api.models.products.response.product_response_models import BaseResponse, CategoryData, ProductData

logger = logging.getLogger(__name__)
category_router = APIRouter(prefix="/category", tags=["Category"])


def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)


@category_router.post("/create", response_model=BaseResponse[ProductCategory], status_code=status.HTTP_201_CREATED)
async def create_category(
        category: CategoryCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        result = await create_category_service(category=category, db=db)
        return BaseResponse(data=result)
    except ValueError as e:
        logger.warning("Validation error creating category: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except IntegrityError as ie:
        logger.warning("Integrity error creating category: %s", ie)
        return error_response("Category with this name already exists", status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error creating category", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@category_router.put("/update/{category_id}", response_model=BaseResponse[ProductCategory])
async def update_category(
        category_id: int,
        category_update: CategoryUpdate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        updated = await update_category_service(category_id, category_update, db)
        if not updated:
            return error_response("Category not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=updated)
    except ValueError as e:
        logger.warning("Validation error updating category %s: %s", category_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except IntegrityError as ie:
        logger.warning("Integrity error updating category %s: %s", category_id, ie)
        return error_response("Category with this name already exists", status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error updating category %s", category_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@category_router.delete("/delete/{category_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
async def delete_category(
        category_id: int,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        result = await delete_category_service(category_id, db)
        if not result:
            return error_response("Category not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(message="Category deleted successfully")
    except Exception as ex:
        logger.error("Error deleting category %s", category_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@category_router.post("/{category_id}/products", response_model=BaseResponse[Product])
async def add_product_to_category(
        category_id: int,
        product: ProductCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        new_product = await add_product_to_category_service(category_id, product, db)
        if not new_product:
            return error_response("Category not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=new_product)
    except ValueError as e:
        logger.warning("Validation error adding product to category %s: %s", category_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except IntegrityError as ie:
        logger.warning("Integrity error adding product to category %s: %s", category_id, ie)
        return error_response("Product with this name already exists", status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error adding product to category %s", category_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@category_router.delete("/{category_id}/products/{product_id}", response_model=BaseResponse[None],
                        status_code=status.HTTP_200_OK)
async def remove_product_from_category(
        category_id: int,
        product_id: int,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        removed = await remove_product_from_category_service(category_id, product_id, db)
        if not removed:
            return error_response("Category or Product not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(message="Product removed from category successfully")
    except Exception as ex:
        logger.error("Error removing product %s from category %s", product_id, category_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@category_router.get(
    "/",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK
)
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Retrieve a paginated list of all product categories.
    """
    try:
        categories = await get_categories_service(db, skip=skip, limit=limit)
        return BaseResponse(data=[CategoryData.model_validate(i) for i in categories])
    except Exception as ex:
        logger.error("Error fetching categories", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)