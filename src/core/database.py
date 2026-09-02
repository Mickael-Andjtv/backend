from sqlmodel import Session, SQLModel, create_engine
from .config import get_settings
from ..models import (
    User,
    Customer,
    CustomerLoyalty,
    CustomerPreferences,
    Category,
    MenuItem,
    MenuOption,
    MenuOptionGroup,
    RestaurantTable,
    Reservation,
    Order,
    OrderItem,
    Payment,
    PromoCode,
)

engine = create_engine(get_settings().DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")


def get_session():
    with Session(engine) as session:
        yield session