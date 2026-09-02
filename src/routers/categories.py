from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
import uuid
from datetime import datetime

from ..models import Category
from ..schemas import CategoryCreateSchema, CategoryUpdateSchema, CategoryResponseSchema
from ..core.database import get_session

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponseSchema])
def get_categories(
    session: Session = Depends(get_session),
    is_active: bool = Query(True),
):
    """Get all categories"""
    statement = select(Category).where(Category.isActive == is_active)
    categories = session.exec(statement).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponseSchema)
def get_category(category_id: str, session: Session = Depends(get_session)):
    """Get a specific category"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("", response_model=CategoryResponseSchema)
def create_category(
    data: CategoryCreateSchema, session: Session = Depends(get_session)
):
    """Create a new category"""
    # Check if category with same name already exists
    existing = session.exec(
        select(Category).where(Category.name == data.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = Category(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        imageUrl=data.imageUrl,
        isActive=True,
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponseSchema)
def update_category(
    category_id: str,
    data: CategoryUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update a category"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    category.updatedAt = datetime.utcnow()
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: str, session: Session = Depends(get_session)):
    """Soft delete a category"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.isActive = False
    category.updatedAt = datetime.utcnow()
    session.add(category)
    session.commit()
    return {"message": "Category deleted"}
