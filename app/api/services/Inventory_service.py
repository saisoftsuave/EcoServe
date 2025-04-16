from typing import Optional, List

from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import Product, Inventory
from app.api.services.warehouse_service import Warehouse
#
#
# class Inventory(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     product_id: int = Field(foreign_key="product.id")
#     warehouse_id: int = Field(foreign_key="warehouse.id")
#     quantity: int

class InventoryCreate(SQLModel):
    product_id: int
    warehouse_id: int
    quantity: int

class InventoryUpdate(SQLModel):
    product_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    quantity: Optional[int] = None

# Create
def create_inventory_service(db: AsyncSession, inventory: InventoryCreate) -> Inventory:
    if not db.get(Product, inventory.product_id):
        raise ValueError("Product not found")
    if not db.get(Warehouse, inventory.warehouse_id):
        raise ValueError("Warehouse not found")
    inventory_model = Inventory(**inventory.dict())
    db.add(inventory_model)
    db.commit()
    db.refresh(inventory_model)
    return inventory_model

# Read One
def get_inventory_service(db: AsyncSession, inventory_id: int) -> Optional[Inventory]:
    return db.get(Inventory, inventory_id)

# Read All
def get_inventories_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Inventory]:
    return db.query(Inventory).offset(skip).limit(limit).all()

# Update
def update_inventory_service(db: AsyncSession, inventory_id: int, inventory_update: InventoryUpdate) -> Optional[Inventory]:
    inventory = db.get(Inventory, inventory_id)
    if inventory:
        for key, value in inventory_update.dict(exclude_unset=True).items():
            if key == "product_id" and value is not None:
                if not db.get(Product, value):
                    raise ValueError("Product not found")
            elif key == "warehouse_id" and value is not None:
                if not db.get(Warehouse, value):
                    raise ValueError("Warehouse not found")
            setattr(inventory, key, value)
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return inventory
    return None

# Delete
def delete_inventory_service(db: AsyncSession, inventory_id: int) -> Optional[Inventory]:
    inventory = db.get(Inventory, inventory_id)
    if inventory:
        db.delete(inventory)
        db.commit()
        return inventory
    return None