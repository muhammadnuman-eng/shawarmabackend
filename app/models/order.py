from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    PREPARING_OLD = "Preparing"  # Keep for backward compatibility
    PICKUP = "Pickup"
    DELIVERING = "Delivering"
    CANCELLED_OLD = "Cancelled"
    DELIVERED_OLD = "Delivered"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class DeliveryType(str, enum.Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # For mobile app users
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)  # For admin panel
    status = Column(String(50), default="pending")  # Changed to String for flexibility
    address_id = Column(String(36), ForeignKey("addresses.id"), nullable=True)
    delivery_type = Column(String(50), default="delivery")  # 'delivery' or 'pickup'
    payment_method = Column(String(100))
    payment_status = Column(String(50), default="pending")
    promo_code = Column(String(50), nullable=True)
    promo_discount = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0)
    platform_fee = Column(Float, default=0.0)
    gst = Column(Float, default=0.0)
    tip = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    location = Column(Text)
    image_url = Column(String(500))
    review_rating = Column(Integer)
    branch = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    delivery_address = relationship("Address", foreign_keys=[address_id])
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="order", uselist=False)
    transaction = relationship("Transaction", back_populates="order", uselist=False)
    tracking = relationship("OrderTracking", back_populates="order", cascade="all, delete-orphan")

class OrderTracking(Base):
    __tablename__ = "order_tracking"
    
    id = Column(String(36), primary_key=True, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    status = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="tracking")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String(36), primary_key=True, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(String(36), ForeignKey("products.id"))
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    additional_data = Column(JSON)  # For storing components, ingredients, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

