from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    menu_item_id: Optional[str] = None
    item_name: str
    quantity: int = 1
    price: float
    additional_data: Optional[dict] = None

class OrderItemResponse(BaseModel):
    id: str
    order_id: str
    menu_item_id: Optional[str]
    item_name: str
    quantity: int
    price: float
    additional_data: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: str
    items: List[OrderItemCreate]
    status: OrderStatus = OrderStatus.PREPARING
    delivery_fee: float = 0.0
    tip: float = 0.0
    location: Optional[str] = None
    image_url: Optional[str] = None
    payment_method: Optional[str] = None
    branch: Optional[str] = None

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_fee: Optional[float] = None
    tip: Optional[float] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    payment_method: Optional[str] = None
    branch: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    order_number: str
    customer_id: str
    customer_name: str
    status: OrderStatus
    amount: float
    delivery_fee: float
    tip: float
    location: Optional[str]
    image_url: Optional[str]
    review_rating: Optional[int]
    payment_method: Optional[str]
    branch: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    order_items: List[OrderItemResponse]
    items: Optional[str] = None  # Combined items string for frontend compatibility
    
    class Config:
        from_attributes = True

