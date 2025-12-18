from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.customer import MembershipType

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    address: Optional[str] = None
    profile_pic: Optional[str] = None
    membership: MembershipType = MembershipType.BRONZE

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    address: Optional[str] = None
    profile_pic: Optional[str] = None
    membership: Optional[MembershipType] = None
    preferred_branch: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    profile_pic: Optional[str]
    membership: MembershipType
    total_orders: int
    total_spent: float
    review_rating: Optional[float]
    preferred_branch: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

