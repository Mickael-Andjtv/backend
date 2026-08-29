from sqlmodel import Session, SQLModel, create_engine
from .config import get_settings
from ..models import *

engine = create_engine(get_settings().DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("created......")


def get_session():
    with Session(engine) as session:
        yield session