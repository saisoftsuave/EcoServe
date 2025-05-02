from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette import status
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from app.api.models.products import ProductImage
from app.api.services.product_image_service import (
    ProductImageCreate,
    create_product_image_service,
    get_product_image_service,
    get_product_images_service,
    update_product_image_service,
    delete_product_image_service,
    ProductImageUpdate
)
from app.core.db import get_db
from app.api.models.products.response.product_response_models import BaseResponse

logger = logging.getLogger(__name__)
product_images_router = APIRouter(prefix="/product-images", tags=["Product Images"])

def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)

@product_images_router.post("/", response_model=BaseResponse[ProductImage], status_code=status.HTTP_201_CREATED)
async def create_product_image(
    image: ProductImageCreate,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[ProductImage]:
    try:
        result = await create_product_image_service(db, image)
        return BaseResponse(data=result)
    except ValueError as e:
        logger.warning("Validation error creating product image: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error creating product image", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@product_images_router.get("/{image_id}", response_model=BaseResponse[ProductImage])
async def read_product_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[ProductImage]:
    try:
        image = await get_product_image_service(db, image_id)
        if not image:
            return error_response("Product image not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=image)
    except Exception as ex:
        logger.error("Error reading product image %s", image_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@product_images_router.get("/", response_model=BaseResponse[List[ProductImage]])
async def read_product_images(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[List[ProductImage]]:
    try:
        images = await get_product_images_service(db, skip=skip, limit=limit)
        return BaseResponse(data=images)
    except Exception as ex:
        logger.error("Error reading product images list", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@product_images_router.put("/{image_id}", response_model=BaseResponse[ProductImage])
async def update_product_image(
    image_id: str,
    image_update: ProductImageUpdate,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[ProductImage]:
    try:
        image = await update_product_image_service(db, image_id, image_update)
        if not image:
            return error_response("Product image not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=image)
    except ValueError as e:
        logger.warning("Validation error updating product image %s: %s", image_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error updating product image %s", image_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@product_images_router.delete("/{image_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
async def delete_product_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[None]:
    try:
        deleted = await delete_product_image_service(db, image_id)
        if not deleted:
            return error_response("Product image not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(message="Product image deleted successfully")
    except Exception as ex:
        logger.error("Error deleting product image %s", image_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)