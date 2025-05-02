from fastapi import APIRouter

from app.api.routes.carts.cart_routes import cart_router
from app.api.routes.orders.order_router import order_router
from app.api.routes.orders.payment_routes import payment_router
from app.api.routes.products.category_routes import category_router
from app.api.routes.products.inventory_routes import inventory_router
from app.api.routes.products.product_images_routes import product_images_router
from app.api.routes.products.product_routes import product_router
from app.api.routes.products.review_routes import reviews_router
from app.api.routes.products.warehouse_routes import warehouses_router
from app.api.routes.user.user_routes import user_router

main_router = APIRouter()

main_router.include_router(router=user_router)
main_router.include_router(router=product_router)
main_router.include_router(router=category_router)
main_router.include_router(router=product_images_router)
main_router.include_router(router=inventory_router)
main_router.include_router(router=warehouses_router)
main_router.include_router(router=reviews_router)
main_router.include_router(router=cart_router)
main_router.include_router(router=order_router)
main_router.include_router(router=payment_router)