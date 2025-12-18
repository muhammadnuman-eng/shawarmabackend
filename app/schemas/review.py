from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    order_id: str
    customer_id: str
    rating: int  # 1-5
    review_text: Optional[str] = None
    branch: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    order_id: Optional[str]
    customer_id: str
    customer_name: str
    rating: int
    review_text: Optional[str]
    branch: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

