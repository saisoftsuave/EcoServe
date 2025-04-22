from typing import Optional, List

from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import Product, ProductImage



class ProductImageCreate(SQLModel):
    product_id: str
    image: str
    primary_image: bool = False


class ProductImageUpdate(SQLModel):
    product_id: Optional[str] = None
    image: Optional[str] = None
    primary_image: Optional[bool] = None


# Create
async def create_product_image_service(db: AsyncSession, product_image: ProductImageCreate) -> ProductImage:
    if not db.get(Product, product_image.product_id):
        raise ValueError("Product not found")
    image_model = ProductImage(**product_image.dict())
    db.add(image_model)
    await db.commit()
    await db.refresh(image_model)
    return image_model


# Read One
async def get_product_image_service(db: AsyncSession, image_id: str) -> Optional[ProductImage]:
    return await db.get(ProductImage, image_id)


# Read All
async def get_product_images_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ProductImage]:
    product_images = await db.execute(statement=select(ProductImage).offset(skip).limit(limit))
    return product_images.scalars().all()


# Update
async def update_product_image_service(db: AsyncSession, image_id: str, image_update: ProductImageUpdate) -> Optional[
    ProductImage]:
    image = await db.get(ProductImage, image_id)
    if image:
        for key, value in image_update.dict(exclude_unset=True).items():
            setattr(image, key, value)
        db.add(image)
        await db.commit()
        await db.refresh(image)
        return image
    return None


# Delete
async def delete_product_image_service(db: AsyncSession, image_id: str) -> Optional[ProductImage]:
    image = await db.get(ProductImage, image_id)
    if image:
        await db.delete(image)
        await db.commit()
        return image
    return None
