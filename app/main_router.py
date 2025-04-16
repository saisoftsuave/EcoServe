from fastapi import APIRouter

from app.api.routes.products.category_routes import category_router
from app.api.routes.products.product_images_routes import product_images_router
from app.api.routes.products.product_routes import product_router
from app.api.routes.user.user_routes import user_router
from app.api.utils.router_tags import USER_ROUTER_TAG
from app.api.utils.routes import USER_ROUTER

main_router = APIRouter()

main_router.include_router(router=user_router, prefix=USER_ROUTER, tags=[USER_ROUTER_TAG])
main_router.include_router(router=product_router)
main_router.include_router(router=category_router)
main_router.include_router(router=product_images_router)