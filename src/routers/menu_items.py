from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, and_
import uuid
from datetime import datetime

from ..models import MenuItem, Category
from ..schemas import (
    MenuItemCreateSchema,
    MenuItemUpdateSchema,
    MenuItemResponseSchema,
)
from ..core.database import get_session

router = APIRouter(prefix="/api/menu-items", tags=["menu-items"])


@router.get("", response_model=list[MenuItemResponseSchema])
def get_menu_items(
    session: Session = Depends(get_session),
    category_id: str = Query(None),
    status: str = Query(None),
):
    """Get all menu items"""
    filters = []
    if category_id:
        filters.append(MenuItem.categoryId == category_id)
    if status:
        filters.append(MenuItem.status == status)
    
    statement = select(MenuItem).where(and_(*filters)) if filters else select(MenuItem)
    items = session.exec(statement).all()
    return items


@router.get("/{item_id}", response_model=MenuItemResponseSchema)
def get_menu_item(item_id: str, session: Session = Depends(get_session)):
    """Get a specific menu item"""
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.post("", response_model=MenuItemResponseSchema)
def create_menu_item(
    data: MenuItemCreateSchema, session: Session = Depends(get_session)
):
    """Create a new menu item"""
    # Check if category exists
    category = session.get(Category, data.categoryId)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    item = MenuItem(
        id=str(uuid.uuid4()),
        categoryId=data.categoryId,
        name=data.name,
        description=data.description,
        price=data.price,
        imageUrl=data.imageUrl or [],
        status=data.status,
        isVegetarian=data.isVegetarian,
        isGlutenFree=data.isGlutenFree,
        preparationTimeMinutes=data.preparationTimeMinutes,
        isActive=True,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{item_id}", response_model=MenuItemResponseSchema)
def update_menu_item(
    item_id: str,
    data: MenuItemUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update a menu item"""
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(item, key, value)
    
    item.updatedAt = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_menu_item(item_id: str, session: Session = Depends(get_session)):
    """Delete a menu item"""
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    session.delete(item)
    session.commit()
    return {"message": "Menu item deleted"}


@router.patch("/{item_id}/status")
def update_menu_item_status(
    item_id: str,
    status: str = Query(...),
    session: Session = Depends(get_session),
):
    """Update menu item status"""
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item.status = status
    item.updatedAt = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
