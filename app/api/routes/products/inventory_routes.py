from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import Inventory
from app.api.services.Inventory_service import InventoryCreate, create_inventory_service, get_inventory_service, \
    get_inventories_service, update_inventory_service, delete_inventory_service, InventoryUpdate
from app.core.db import get_db

inventory_router = APIRouter(prefix="/inventory", tags=["Inventory"])

@inventory_router.post("/", response_model=Inventory, status_code=201)
async def create_inventory(inventory: InventoryCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_inventory_service(db, inventory)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@inventory_router.get("/{inventory_id}", response_model=Inventory)
async def read_inventory(inventory_id: int, db: AsyncSession = Depends(get_db)):
    inventory = await get_inventory_service(db, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@inventory_router.get("/", response_model=List[Inventory])
async def read_inventories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return get_inventories_service(db, skip=skip, limit=limit)

@inventory_router.put("/{inventory_id}", response_model=Inventory)
async def update_inventory(inventory_id: int, inventory_update: InventoryUpdate, db: AsyncSession = Depends(get_db)):
    try:
        inventory = await update_inventory_service(db, inventory_id, inventory_update)
        if inventory is None:
            raise HTTPException(status_code=404, detail="Inventory not found")
        return inventory
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@inventory_router.delete("/{inventory_id}", status_code=204)
async def delete_inventory(inventory_id: int, db: AsyncSession = Depends(get_db)):
    if await delete_inventory_service(db, inventory_id) is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return None