from fastapi import APIRouter

from app.api.routes.user.user_routes import user_router
from app.api.utils.router_tags import USER_ROUTER_TAG
from app.api.utils.routes import USER_ROUTER

main_router = APIRouter()

main_router.include_router(router=user_router, prefix=USER_ROUTER, tags=[USER_ROUTER_TAG])
