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

