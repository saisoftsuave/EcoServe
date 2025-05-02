from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.api.models.products.db.product_category import ProductCategory
from app.api.models.products.db.product import Product
from app.api.models.products.category_request import CategoryCreate, CategoryUpdate

# Custom exceptions
class CategoryServiceError(Exception):
    """Base exception for category service operations."""
    pass

class CategoryNotFoundError(CategoryServiceError):
    pass

class DuplicateCategoryError(CategoryServiceError):
    pass

class ProductAssignmentError(CategoryServiceError):
    pass

async def create_category_service(category: CategoryCreate, db: AsyncSession) -> ProductCategory:
    category_model = ProductCategory(**category.dict())
    db.add(category_model)
    try:
        await db.commit()
        await db.refresh(category_model)
    except IntegrityError:
        await db.rollback()
        raise DuplicateCategoryError(f"Category with name '{category.name}' already exists")
    except Exception:
        await db.rollback()
        raise CategoryServiceError("Failed to create category")
    return category_model

async def update_category_service(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession
) -> ProductCategory:
    category = await db.get(ProductCategory, category_id)
    if not category:
        raise CategoryNotFoundError(f"Category id {category_id} not found")
    update_data = category_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.add(category)
    try:
        await db.commit()
        await db.refresh(category)
    except IntegrityError:
        await db.rollback()
        raise DuplicateCategoryError(f"Category with name '{update_data.get('name')}' already exists")
    except Exception:
        await db.rollback()
        raise CategoryServiceError("Failed to update category")
    return category

async def delete_category_service(category_id: int, db: AsyncSession) -> ProductCategory:
    category = await db.get(ProductCategory, category_id)
    if not category:
        raise CategoryNotFoundError(f"Category id {category_id} not found")
    try:
        await db.delete(category)
        await db.commit()
    except Exception:
        await db.rollback()
        raise CategoryServiceError("Failed to delete category")
    return category

async def add_product_to_category_service(
    category_id: int,
    product_data: CategoryCreate,
    db: AsyncSession
) -> Product:
    category = await db.get(ProductCategory, category_id)
    if not category:
        raise CategoryNotFoundError(f"Category id {category_id} not found")
    product_model = Product(**{**product_data.dict(), 'category_id': category_id})
    db.add(product_model)
    try:
        await db.commit()
        await db.refresh(product_model)
    except IntegrityError:
        await db.rollback()
        raise DuplicateCategoryError(f"Product with name '{product_model.name}' already exists in this category")
    except Exception:
        await db.rollback()
        raise ProductAssignmentError("Failed to assign product to category")
    return product_model

async def remove_product_from_category_service(
    category_id: int,
    product_id: int,
    db: AsyncSession
) -> Product:
    category = await db.get(ProductCategory, category_id)
    if not category:
        raise CategoryNotFoundError(f"Category id {category_id} not found")
    product = await db.get(Product, product_id)
    if not product or product.category_id != category_id:
        raise ProductAssignmentError(f"Product id {product_id} not found in category {category_id}")
    try:
        await db.delete(product)
        await db.commit()
    except Exception:
        await db.rollback()
        raise CategoryServiceError("Failed to remove product from category")
    return product


async def get_categories_service(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[ProductCategory]:
    """
    Fetch a paginated list of all product categories.
    """
    statement = select(ProductCategory).offset(skip).limit(limit)
    result = await db.execute(statement)
    categories = result.scalars().all()
    return categories