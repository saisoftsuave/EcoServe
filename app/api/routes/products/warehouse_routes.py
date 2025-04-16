from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import Warehouse
from app.api.services.warehouse_service import WarehouseCreate, create_warehouse_service, \
    delete_warehouse_service, update_warehouse_service, get_warehouses_service, get_warehouse_service, WarehouseUpdate
from app.core.db import get_db

warehouses_router = APIRouter(prefix="/warehouses", tags=["Warehouses"])

@warehouses_router.post("/", response_model=Warehouse, status_code=201)
async def create_warehouse(warehouse: WarehouseCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_warehouse_service(db, warehouse)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Warehouse with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@warehouses_router.get("/{warehouse_id}", response_model=Warehouse)
async def read_warehouse(warehouse_id: str, db: AsyncSession = Depends(get_db)):
    warehouse = await get_warehouse_service(db, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@warehouses_router.get("/", response_model=List[Warehouse])
async def read_warehouses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_warehouses_service(db, skip=skip, limit=limit)

@warehouses_router.put("/{warehouse_id}", response_model=Warehouse)
async def update_warehouse(warehouse_id: str, warehouse_update: WarehouseUpdate, db: AsyncSession = Depends(get_db)):
    try:
        warehouse = await update_warehouse_service(db, warehouse_id, warehouse_update)
        if warehouse is None:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        return warehouse
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Warehouse with this name already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@warehouses_router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(warehouse_id: str, db: AsyncSession = Depends(get_db)):
    if await delete_warehouse_service(db, warehouse_id) is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return None