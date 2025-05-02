from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette import status
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from app.api.models.products import Inventory
from app.api.services.Inventory_service import (
    InventoryCreate,
    create_inventory_service,
    get_inventory_service,
    get_inventories_service,
    update_inventory_service,
    delete_inventory_service,
    InventoryUpdate
)
from app.core.db import get_db
from app.api.models.products.response.product_response_models import BaseResponse

logger = logging.getLogger(__name__)
inventory_router = APIRouter(prefix="/inventory", tags=["Inventory"])

def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)

@inventory_router.post("/", response_model=BaseResponse[Inventory], status_code=status.HTTP_201_CREATED)
async def create_inventory(
    inventory: InventoryCreate,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[Inventory]:
    try:
        result = await create_inventory_service(db, inventory)
        return BaseResponse(data=result)
    except ValueError as e:
        logger.warning("Validation error creating inventory: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error creating inventory", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@inventory_router.get("/{inventory_id}", response_model=BaseResponse[Inventory])
async def read_inventory(
    inventory_id: int,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[Inventory]:
    try:
        inventory = await get_inventory_service(db, inventory_id)
        if not inventory:
            return error_response("Inventory not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=inventory)
    except Exception as ex:
        logger.error("Error reading inventory %s", inventory_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@inventory_router.get("/", response_model=BaseResponse[List[Inventory]])
async def read_inventories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[List[Inventory]]:
    try:
        items = await get_inventories_service(db, skip=skip, limit=limit)
        return BaseResponse(data=items)
    except Exception as ex:
        logger.error("Error reading inventories list", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@inventory_router.put("/{inventory_id}", response_model=BaseResponse[Inventory])
async def update_inventory(
    inventory_id: int,
    inventory_update: InventoryUpdate,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[Inventory]:
    try:
        inv = await update_inventory_service(db, inventory_id, inventory_update)
        if not inv:
            return error_response("Inventory not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=inv)
    except ValueError as e:
        logger.warning("Validation error updating inventory %s: %s", inventory_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error updating inventory %s", inventory_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@inventory_router.delete("/{inventory_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
async def delete_inventory(
    inventory_id: int,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse[None]:
    try:
        deleted = await delete_inventory_service(db, inventory_id)
        if not deleted:
            return error_response("Inventory not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(message="Inventory deleted successfully")
    except Exception as ex:
        logger.error("Error deleting inventory %s", inventory_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)