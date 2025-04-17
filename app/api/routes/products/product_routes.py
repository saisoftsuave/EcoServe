from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products.db.product import Product
from app.api.models.products.product_request import ProductCreate, ProductUpdate
from app.api.services.product_service import create_product_service, \
    get_product_service, get_products_service, update_product_service, delete_product_service
from app.api.routes.user.user_service import get_current_user
from app.core.db import get_db

product_router = APIRouter(prefix="/products", tags=["Products"])

"""
Note : Will add role like merchant and customer
"""


@product_router.post("/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await create_product_service(db, product)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@product_router.get("/{product_id}", response_model=Product)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = get_product_service(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


"""
Note:for performance only returning the primary image and minimal details
"""


@product_router.get("/", response_model=List[Product])
async def read_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_products_service(db, skip=skip, limit=limit)


@product_router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_db),
                         user=Depends(get_current_user)):
    try:
        product = update_product_service(db, product_id, product_update)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@product_router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if delete_product_service(db, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
