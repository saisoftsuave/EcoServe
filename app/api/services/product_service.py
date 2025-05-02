from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products.db.product import Product
from app.api.models.products.db.product_category import ProductCategory
from app.api.models.products.product_request import ProductCreate, ProductUpdate

# Custom exceptions
class ProductServiceError(Exception):
    """Base exception for product service."""
    pass

class CategoryNotFoundError(ProductServiceError):
    pass

class ProductNotFoundError(ProductServiceError):
    pass

class DuplicateProductError(ProductServiceError):
    pass

async def create_product_service(db: AsyncSession, product: ProductCreate) -> Product:
    # Ensure category exists
    category = await db.get(ProductCategory, product.category_id)
    if not category:
        raise CategoryNotFoundError(f"Category id {product.category_id} not found")
    product_model = Product(**product.dict())
    db.add(product_model)
    try:
        await db.commit()
        await db.refresh(product_model)
    except IntegrityError:
        await db.rollback()
        raise DuplicateProductError("Product with this name already exists")
    except Exception:
        await db.rollback()
        raise ProductServiceError("Failed to create product")
    return product_model

async def get_product_service(db: AsyncSession, product_id: str) -> Optional[Product]:
    product = await db.get(Product, product_id)
    if not product:
        raise ProductNotFoundError(f"Product id {product_id} not found")
    return product

async def get_products_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Product]:
    stmt = select(Product).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_products_by_name_service(
    db: AsyncSession, name_filter: str, skip: int = 0, limit: int = 100
) -> List[Product]:
    stmt = (
        select(Product)
        .options(selectinload(Product.reviews))
        .where(Product.name.ilike(f"%{name_filter}%"))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_product_service(
    db: AsyncSession, product_id: str, product_update: ProductUpdate
) -> Optional[Product]:
    product = await db.get(Product, product_id)
    if not product:
        raise ProductNotFoundError(f"Product id {product_id} not found")
    update_data = product_update.dict(exclude_unset=True)
    if "category_id" in update_data:
        category = await db.get(ProductCategory, update_data["category_id"])
        if not category:
            raise CategoryNotFoundError(f"Category id {update_data['category_id']} not found")
    for key, value in update_data.items():
        setattr(product, key, value)
    db.add(product)
    try:
        await db.commit()
        await db.refresh(product)
    except IntegrityError:
        await db.rollback()
        raise DuplicateProductError("Product with this name already exists")
    except Exception:
        await db.rollback()
        raise ProductServiceError("Failed to update product")
    return product

async def delete_product_service(db: AsyncSession, product_id: str) -> Optional[Product]:
    product = await db.get(Product, product_id)
    if not product:
        raise ProductNotFoundError(f"Product id {product_id} not found")
    try:
        await db.delete(product)
        await db.commit()
    except Exception:
        await db.rollback()
        raise ProductServiceError("Failed to delete product")
    return product
