from contextlib import asynccontextmanager

from fastapi import FastAPI

# from .api.api_v1.api import api_router
from .core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="STOCK-API")