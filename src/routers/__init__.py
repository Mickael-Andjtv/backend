from .categories import router as categories_router
from .auth import router as auth_router
from .menu_items import router as menu_items_router
from .customers import router as customers_router
from .tables import router as tables_router
from .orders import router as orders_router
from .reservations import router as reservations_router
from .dashboard import router as dashboard_router
from .uploads import router as uploads_router
from .notifications import router as notifications_router
from .invoices import router as invoices_router

__all__ = [
    "categories_router",
    "auth_router",
    "menu_items_router",
    "customers_router",
    "tables_router",
    "orders_router",
    "reservations_router",
    "dashboard_router",
    "uploads_router",
    "notifications_router",
    "invoices_router",
]
