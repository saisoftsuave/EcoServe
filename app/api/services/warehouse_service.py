from typing import Optional, List

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import Warehouse, Product


class WarehouseCreate(SQLModel):
    name: str
    address: Optional[str] = None


class WarehouseUpdate(SQLModel):
    name: Optional[str] = None
    address: Optional[str] = None


# Create
async def create_warehouse_service(db: AsyncSession, warehouse: WarehouseCreate) -> Warehouse:
    warehouse_model = Warehouse(**warehouse.dict())
    db.add(warehouse_model)
    await db.commit()
    await db.refresh(warehouse_model)
    return warehouse_model


# Read One
async def get_warehouse_service(db: AsyncSession, warehouse_id: str) -> Optional[Warehouse]:
    return await db.get(Warehouse, warehouse_id)


# Read All
async def get_warehouses_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Warehouse]:
    warehouses = await db.execute(statement=select(Warehouse).offset(skip).limit(limit))
    return warehouses.scalars().all()


# Update
async def update_warehouse_service(db: AsyncSession, warehouse_id: str, warehouse_update: WarehouseUpdate) -> Optional[
    Warehouse]:
    warehouse = await db.get(Warehouse, warehouse_id)
    if warehouse:
        for key, value in warehouse_update.dict(exclude_unset=True).items():
            setattr(warehouse, key, value)
        db.add(warehouse)
        await db.commit()
        await db.refresh(warehouse)
        return warehouse
    return None


# Delete
def delete_warehouse_service(db: AsyncSession, warehouse_id: str) -> Optional[Warehouse]:
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse:
        db.delete(warehouse)
        db.commit()
        return warehouse
    return None
