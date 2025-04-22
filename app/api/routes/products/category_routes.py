from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import ProductCategory
from app.api.models.products.category_request import CategoryCreate
from app.api.services.category_service import create_category_service, delete_category_service
from app.api.routes.user.user_service import get_current_user
from app.core.db import get_db

category_router = APIRouter(prefix="/category", tags=["Category"])


@category_router.post("/create", response_model=ProductCategory, status_code=201)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await create_category_service(category=category, db=db)
        print(result)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.delete("/delete", response_model=ProductCategory, status_code=403)
async def delete_category(category_id: str, db: AsyncSession = Depends(get_db)):
    if await delete_category_service(category_id, db) is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return None
