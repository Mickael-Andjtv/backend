from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from ..enums import PAYEMENTMETHOD, PAYEMENTSTATUS

class Payement(SQLModel):
    amount:float
    method:PAYEMENTMETHOD = PAYEMENTMETHOD.CARD
    status:PAYEMENTSTATUS = PAYEMENTSTATUS.PENDING
    paid_at:datetime = Field(default_factory=datetime.now)

class PayementDB(Payement, table=True):
    __tablename__ ='payements'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id:UUID|None = Field(None, foreign_key='orders.id')
