from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DashboardStats(BaseModel):
    total_orders: int
    total_delivery: int
    cancelled_orders: int
    total_revenue: float
    today_revenue: float
    refunds: float
    orders_change_percent: Optional[str] = None
    delivery_change_percent: Optional[str] = None
    cancelled_change_percent: Optional[str] = None
    revenue_change_percent: Optional[str] = None

class ActiveOrderResponse(BaseModel):
    id: str
    order_number: str
    customer_name: str
    status: str
    items: str
    amount: float
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class EarningBreakdownResponse(BaseModel):
    food_sales: float
    delivery_fees: float
    tips: float
    total_revenue: float

class StaffListResponse(BaseModel):
    id: str
    name: str
    location: str
    role: str
    profile_pic: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TopCustomerResponse(BaseModel):
    id: str
    name: str
    membership: str
    orders: int
    total_spent: float
    profile_pic: Optional[str]

    class Config:
        from_attributes = True

