from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import ProductImage
from app.api.services.product_image_service import ProductImageCreate, create_product_image_service, \
    get_product_image_service, get_product_images_service, update_product_image_service, delete_product_image_service, \
    ProductImageUpdate
from app.core.db import get_db

product_images_router = APIRouter(prefix="/product-images", tags=["Product Images"])


@product_images_router.post("/", response_model=ProductImage, status_code=201)
async def create_product_image(image: ProductImageCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_product_image_service(db, image)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@product_images_router.get("/{image_id}", response_model=ProductImage)
async def read_product_image(image_id: str, db: AsyncSession = Depends(get_db)):
    image = await get_product_image_service(db, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    return image


@product_images_router.get("/", response_model=List[ProductImage])
async def read_product_images(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_product_images_service(db, skip=skip, limit=limit)


@product_images_router.put("/{image_id}", response_model=ProductImage)
async def update_product_image(image_id: str, image_update: ProductImageUpdate, db: AsyncSession = Depends(get_db)):
    try:
        image = await update_product_image_service(db, image_id, image_update)
        if image is None:
            raise HTTPException(status_code=404, detail="Product image not found")
        return image
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@product_images_router.delete("/{image_id}", status_code=204)
async def delete_product_image(image_id: str, db: AsyncSession = Depends(get_db)):
    if await delete_product_image_service(db, image_id) is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    return None
