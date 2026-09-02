from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
import uuid
from datetime import datetime

from ..models import RestaurantTable
from ..schemas import TableCreateSchema, TableUpdateSchema, TableResponseSchema
from ..core.database import get_session

router = APIRouter(prefix="/api/tables", tags=["tables"])


@router.get("", response_model=list[TableResponseSchema])
def get_tables(
    session: Session = Depends(get_session),
    status: str = Query(None),
):
    """Get all restaurant tables"""
    query = select(RestaurantTable)
    if status:
        query = query.where(RestaurantTable.status == status)
    
    tables = session.exec(query).all()
    return tables


@router.get("/{table_id}", response_model=TableResponseSchema)
def get_table(table_id: str, session: Session = Depends(get_session)):
    """Get a specific table"""
    table = session.get(RestaurantTable, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.post("", response_model=TableResponseSchema)
def create_table(
    data: TableCreateSchema, session: Session = Depends(get_session)
):
    """Create a new table"""
    # Check if table number already exists
    existing = session.exec(
        select(RestaurantTable).where(RestaurantTable.num == data.num)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Table number already exists")

    table = RestaurantTable(
        id=str(uuid.uuid4()),
        num=data.num,
        capacity=data.capacity,
        place=data.place,
        status="AVAILABLE",
    )
    session.add(table)
    session.commit()
    session.refresh(table)
    return table


@router.put("/{table_id}", response_model=TableResponseSchema)
def update_table(
    table_id: str,
    data: TableUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update a table"""
    table = session.get(RestaurantTable, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Check if new table number already exists
    if data.num and data.num != table.num:
        existing = session.exec(
            select(RestaurantTable).where(RestaurantTable.num == data.num)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Table number already exists")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(table, key, value)
    
    table.updatedAt = datetime.utcnow()
    session.add(table)
    session.commit()
    session.refresh(table)
    return table


@router.delete("/{table_id}")
def delete_table(table_id: str, session: Session = Depends(get_session)):
    """Delete a table"""
    table = session.get(RestaurantTable, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    session.delete(table)
    session.commit()
    return {"message": "Table deleted"}


@router.patch("/{table_id}/status")
def update_table_status(
    table_id: str,
    status: str = Query(...),
    session: Session = Depends(get_session),
):
    """Update table status"""
    table = session.get(RestaurantTable, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table.status = status
    table.updatedAt = datetime.utcnow()
    session.add(table)
    session.commit()
    session.refresh(table)
    return table
