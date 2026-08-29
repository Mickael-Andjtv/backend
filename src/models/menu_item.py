from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel,JSON, Column

class MenuItem(SQLModel):
    name:str
    description:str
    price:float
    category:str
    image:tuple[str, str,str]|None = Field(None, sa_column=Column(JSON))
    available:bool
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MenuItemDB(MenuItem, table=True):
    __tablename__ = 'menu_items'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_item_id:UUID|None = Field(None, foreign_key='order_items.id')
    