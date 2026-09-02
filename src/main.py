from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import create_db_and_tables
from .routers import (
    categories_router,
    menu_items_router,
    customers_router,
    tables_router,
    orders_router,
    reservations_router,
    dashboard_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Restaurant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(categories_router)
app.include_router(menu_items_router)
app.include_router(customers_router)
app.include_router(tables_router)
app.include_router(orders_router)
app.include_router(reservations_router)
app.include_router(dashboard_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Restaurant API"}
