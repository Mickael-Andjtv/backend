from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from datetime import datetime, timedelta

from ..models import Order, Customer, Reservation, MenuItem, OrderItem
from ..core.database import get_session

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    """Get dashboard statistics"""
    # Total customers
    total_customers = session.exec(select(func.count(Customer.id))).one()
    
    # Total orders
    total_orders = session.exec(select(func.count(Order.id))).one()
    
    # Total revenue
    total_revenue = session.exec(select(func.sum(Order.totalAmount))).one() or 0.0
    
    # Orders today
    today = datetime.utcnow().date()
    orders_today = session.exec(
        select(func.count(Order.id)).where(
            func.date(Order.createdAt) == today
        )
    ).one()
    
    # Revenue today
    revenue_today = session.exec(
        select(func.sum(Order.totalAmount)).where(
            func.date(Order.createdAt) == today
        )
    ).one() or 0.0
    
    # Pending orders
    pending_orders = session.exec(
        select(func.count(Order.id)).where(Order.status == "PENDING")
    ).one()
    
    # Pending reservations
    pending_reservations = session.exec(
        select(func.count(Reservation.id)).where(Reservation.status == "PENDING")
    ).one()

    return {
        "totalCustomers": total_customers,
        "totalOrders": total_orders,
        "totalRevenue": total_revenue,
        "ordersToday": orders_today,
        "revenueToday": revenue_today,
        "pendingOrders": pending_orders,
        "pendingReservations": pending_reservations,
    }


@router.get("/orders-by-status")
def get_orders_by_status(session: Session = Depends(get_session)):
    """Get orders grouped by status"""
    orders = session.exec(select(Order)).all()
    status_counts = {}
    
    for order in orders:
        status_counts[order.status] = status_counts.get(order.status, 0) + 1
    
    return status_counts


@router.get("/revenue-by-date")
def get_revenue_by_date(days: int = 30, session: Session = Depends(get_session)):
    """Get revenue for the last N days"""
    data = []
    
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        revenue = session.exec(
            select(func.sum(Order.totalAmount)).where(
                func.date(Order.createdAt) == date
            )
        ).one() or 0.0
        
        data.append({
            "date": date.isoformat(),
            "revenue": revenue,
        })
    
    return data


@router.get("/popular-items")
def get_popular_items(limit: int = 10, session: Session = Depends(get_session)):
    """Get top selling menu items"""
    # Aggregate per menuItemId (no JSON column in grouping)
    statement = (
        select(
            OrderItem.menuItemId,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.totalPrice).label("total_revenue")
        )
        .group_by(OrderItem.menuItemId)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
    )

    results = session.exec(statement).all()
    items = {item.id: item for item in session.exec(select(MenuItem)).all()}

    return [
        {
            "id": row.menuItemId,
            "name": items[row.menuItemId].name if row.menuItemId in items else "N/A",
            "price": items[row.menuItemId].price if row.menuItemId in items else 0.0,
            "imageUrl": items[row.menuItemId].imageUrl if row.menuItemId in items else [],
            "totalQuantity": row.total_quantity,
            "totalRevenue": row.total_revenue,
        }
        for row in results
    ]


@router.get("/reservations-by-date")
def get_reservations_by_date(days: int = 30, session: Session = Depends(get_session)):
    """Get reservations for the last N days"""
    data = []
    
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        count = session.exec(
            select(func.count(Reservation.id)).where(
                Reservation.reservationDate == date
            )
        ).one()
        
        data.append({
            "date": date.isoformat(),
            "count": count,
        })
    
    return data
