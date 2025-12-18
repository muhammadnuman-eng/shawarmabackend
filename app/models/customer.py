from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class MembershipType(str, enum.Enum):
    GOLD = "Gold Members"
    SILVER = "Silver Members"
    BRONZE = "Bronze Members"

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), index=True)
    email = Column(String(255), index=True)
    address = Column(Text)
    profile_pic = Column(String(500))
    membership = Column(Enum(MembershipType), default=MembershipType.BRONZE)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    review_rating = Column(Float)
    preferred_branch = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")

