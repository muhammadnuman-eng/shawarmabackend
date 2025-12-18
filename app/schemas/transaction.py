from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionStatus, PaymentMethod

class TransactionCreate(BaseModel):
    order_id: str
    amount: float
    payment_method: Optional[PaymentMethod] = None
    status: TransactionStatus = TransactionStatus.PENDING
    branch: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    order_id: str
    order_number: str
    amount: float
    payment_method: Optional[PaymentMethod]
    status: TransactionStatus
    branch: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

