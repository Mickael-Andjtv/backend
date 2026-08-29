from sqlmodel import SQLModel, Field
from datetime import datetime
from ..enums import USERROLE

class User(SQLModel):
    email:str = Field(unique=True, primary_key=True)
    full_name:str
    password:str
    phone:str
    address:str
    role:USERROLE = USERROLE.CUSTOMER
    created_at:datetime = Field(default_factory=datetime.now)
    update_at:datetime = Field(default_factory=datetime.now)

class UserDB(User, table=True):
    __tablename__ = 'users'
    
    