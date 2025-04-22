from sqlite3 import IntegrityError
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.cart.cart_request import AddToCart, UpdateCartQuantity
from app.api.models.cart.db.cart import Cart
from app.api.models.products import Product
from app.api.routes.user.user_service import get_current_user
from app.api.services.cart_service import add_to_cart_service, remove_from_cart_service, \
    increase_cart_product_quantity_service, get_cart_service
from app.core.db import get_db

cart_router = APIRouter(prefix="/cart", tags=["cart"])


# @cart_router.post("/add", response_model=List[], status_code=201)
# async def add_to_cart(cart: List[AddToCart], db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
#     try:
#         result = []
#         for i in cart:
#             p = await create_cart_service(db, i)
#             result.append(p)
#         return result
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except IntegrityError:
#         raise HTTPException(status_code=400, detail="cart with this name already exists")
#     except Exception:
#         raise HTTPException(status_code=500, detail="Internal server error")


@cart_router.post("/", response_model=Cart, status_code=201)
async def add_to_cart(request: AddToCart, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        request.user_id = user.id
        result = await add_to_cart_service(db, request)
        print("cart added", result)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="cart with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@cart_router.delete("/{cart_id}", status_code=204)
async def delete_product(cart_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        if await remove_from_cart_service(db, cart_id) is None:
            raise HTTPException(status_code=404, detail="Cart Item not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@cart_router.put("/{cart_id}", response_model=Cart)
async def update_product(cart_id: str, cart_update: UpdateCartQuantity, db: AsyncSession = Depends(get_db),
                         user=Depends(get_current_user)):
    try:
        cart = await increase_cart_product_quantity_service(db, cart_update, cart_id)
        if cart is None:
            raise HTTPException(status_code=404, detail="Cart not found")
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@cart_router.get("/", response_model=List[Product], status_code=200)
async def get_cart(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await get_cart_service(db, user.id)
        price = sum(i.price for i in result)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
