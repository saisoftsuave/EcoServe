from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products.db.inventory import Inventory
from app.api.models.products.db.product import Product
from app.api.services.warehouse_service import Warehouse

# Custom exceptions
class InventoryServiceError(Exception):
    """Base exception for inventory service operations."""
    pass

class InventoryNotFoundError(InventoryServiceError):
    pass

class ProductNotFoundError(InventoryServiceError):
    pass

class WarehouseNotFoundError(InventoryServiceError):
    pass

class DuplicateInventoryError(InventoryServiceError):
    pass

class InventoryCreate(SQLModel):  # if separate, adjust import accordingly
    product_id: int
    warehouse_id: int
    quantity: int

class InventoryUpdate(SQLModel):
    product_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    quantity: Optional[int] = None

# Create
async def create_inventory_service(db: AsyncSession, inventory_data: InventoryCreate) -> Inventory:
    # Validate product
    product = await db.get(Product, inventory_data.product_id)
    if not product:
        raise ProductNotFoundError(f"Product id {inventory_data.product_id} not found")
    # Validate warehouse
    warehouse = await db.get(Warehouse, inventory_data.warehouse_id)
    if not warehouse:
        raise WarehouseNotFoundError(f"Warehouse id {inventory_data.warehouse_id} not found")
    inventory_model = Inventory(**inventory_data.dict())
    db.add(inventory_model)
    try:
        await db.commit()
        await db.refresh(inventory_model)
    except IntegrityError:
        await db.rollback()
        raise DuplicateInventoryError("Inventory record already exists")
    except Exception:
        await db.rollback()
        raise InventoryServiceError("Failed to create inventory")
    return inventory_model

# Read One
async def get_inventory_service(db: AsyncSession, inventory_id: int) -> Inventory:
    inventory = await db.get(Inventory, inventory_id)
    if not inventory:
        raise InventoryNotFoundError(f"Inventory id {inventory_id} not found")
    return inventory

# Read All
async def get_inventories_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Inventory]:
    stmt = select(Inventory).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# Update
async def update_inventory_service(
    db: AsyncSession,
    inventory_id: int,
    inventory_update: InventoryUpdate
) -> Inventory:
    inventory = await db.get(Inventory, inventory_id)
    if not inventory:
        raise InventoryNotFoundError(f"Inventory id {inventory_id} not found")
    update_data = inventory_update.dict(exclude_unset=True)
    # Validate related fields
    if "product_id" in update_data:
        product = await db.get(Product, update_data["product_id"])
        if not product:
            raise ProductNotFoundError(f"Product id {update_data['product_id']} not found")
    if "warehouse_id" in update_data:
        warehouse = await db.get(Warehouse, update_data["warehouse_id"])
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse id {update_data['warehouse_id']} not found")
    # Apply updates
    for key, value in update_data.items():
        setattr(inventory, key, value)
    db.add(inventory)
    try:
        await db.commit()
        await db.refresh(inventory)
    except Exception:
        await db.rollback()
        raise InventoryServiceError("Failed to update inventory")
    return inventory

# Delete
async def delete_inventory_service(db: AsyncSession, inventory_id: int) -> Inventory:
    inventory = await db.get(Inventory, inventory_id)
    if not inventory:
        raise InventoryNotFoundError(f"Inventory id {inventory_id} not found")
    try:
        await db.delete(inventory)
        await db.commit()
    except Exception:
        await db.rollback()
        raise InventoryServiceError("Failed to delete inventory")
    return inventory