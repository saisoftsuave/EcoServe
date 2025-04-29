from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import ProductCategory, Product
from app.api.models.products.category_request import CategoryCreate, CategoryUpdate
from app.api.models.products.product_request import ProductCreate
from app.api.services.category_service import (
    create_category_service,
    delete_category_service,
    update_category_service,
    add_product_to_category_service,
    remove_product_from_category_service
)
from app.api.routes.user.user_service import get_current_user
from app.core.db import get_db

category_router = APIRouter(prefix="/category", tags=["Category"])


@category_router.post("/create", response_model=ProductCategory, status_code=201)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await create_category_service(category=category, db=db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.put("/update/{category_id}", response_model=ProductCategory)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        updated_category = await update_category_service(category_id, category_update, db)
        if updated_category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated_category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.delete("/delete/{category_id}", status_code=204)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await delete_category_service(category_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return None


@category_router.post("/{category_id}/products", response_model=Product)
async def add_product_to_category(
    category_id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        new_product = await add_product_to_category_service(category_id, product, db)
        if new_product is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return new_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.delete("/{category_id}/products/{product_id}", status_code=204)
async def remove_product_from_category(
    category_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    result = await remove_product_from_category_service(category_id, product_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="Category or Product not found")
    return None