from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products.db.product import Product
from app.api.models.products.db.product_category import ProductCategory
from app.api.models.products.product_request import ProductCreate, ProductUpdate


async def create_product_service(db: AsyncSession, product: ProductCreate) -> Product:
    if not await db.get(ProductCategory, product.category_id):
        raise ValueError("Category not found")
    product_model = Product(**product.dict())
    print(product_model)
    db.add(product_model)
    await db.commit()
    await db.refresh(product_model)
    return product_model


async def get_product_service(db: AsyncSession, product_id: int) -> Optional[Product]:
    return await db.get(Product, product_id)

async def get_products_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Product]:
    products = await db.execute(statement=select(Product).offset(skip).limit(limit))
    return products.scalars().all()

async def update_product_service(db: AsyncSession, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    product = db.get(Product, product_id)
    if product:
        for key, value in product_update.dict(exclude_unset=True).items():
            if key == "category_id" and value is not None:
                if not db.get(ProductCategory, value):
                    raise ValueError("Category not found")
            setattr(product, key, value)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    return None

async def delete_product_service(db: AsyncSession, product_id: int) -> Optional[Product]:
    product = db.get(Product, product_id)
    if product:
        await db.delete(product)
        await db.commit()
        return product
    return None