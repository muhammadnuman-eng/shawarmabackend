from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String(36), primary_key=True, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True, unique=True)
    product_id = Column(String(36), ForeignKey("menu_items.id"), nullable=True)  # For product reviews
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # For mobile app users
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)  # For admin panel
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)  # Changed from review_text
    review_text = Column(Text)  # Keep for backward compatibility
    images = Column(JSON)  # Array of image URLs
    helpful_count = Column(Integer, default=0)
    branch = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="review")
    user = relationship("User", back_populates="reviews")
    customer = relationship("Customer", back_populates="reviews")
    product = relationship("MenuItem", foreign_keys=[product_id], overlaps="reviews")

