from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import ProductCategory
from app.api.models.products.category_request import CategoryCreate


async def create_category_service(category: CategoryCreate,db :AsyncSession):
    category_model = ProductCategory(**category.dict())
    db.add(category_model)
    await db.commit()
    await db.refresh(category_model)
    return category_model