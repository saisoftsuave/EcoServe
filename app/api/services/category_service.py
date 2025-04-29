from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import ProductCategory, Product
from app.api.models.products.category_request import CategoryCreate, CategoryUpdate
from app.api.models.products.product_request import ProductCreate


async def create_category_service(category: CategoryCreate, db: AsyncSession):
    category_model = ProductCategory(**category.dict())
    db.add(category_model)
    await db.commit()
    await db.refresh(category_model)
    return category_model


async def update_category_service(category_id: int, category_update: CategoryUpdate, db: AsyncSession):
    category = await db.get(ProductCategory, category_id)
    if not category:
        return None
    update_data = category_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category_service(category_id: int, db: AsyncSession):
    category = await db.get(ProductCategory, category_id)
    if category:
        await db.delete(category)
        await db.commit()
        return category
    return None


async def add_product_to_category_service(category_id: int, product: ProductCreate, db: AsyncSession):
    category = await db.get(ProductCategory, category_id)
    if not category:
        return None
    product_data = product.dict()
    product_data['category_id'] = category_id
    product_model = Product(**product_data)
    db.add(product_model)
    await db.commit()
    await db.refresh(product_model)
    return product_model


async def remove_product_from_category_service(category_id: int, product_id: int, db: AsyncSession):
    category = await db.get(ProductCategory, category_id)
    if not category:
        return None
    product = await db.get(Product, product_id)
    if not product or product.category_id != category_id:
        return None
    await db.delete(product)
    await db.commit()
    return product