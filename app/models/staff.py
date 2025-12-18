from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class StaffStatus(str, enum.Enum):
    ON_DUTY = "On-Duty"
    OFF_DUTY = "Off Duty"

class StaffRole(str, enum.Enum):
    MANAGER = "Manager"
    CHEF = "Chef"
    RIDER = "Rider"
    CASHIER = "Cashier"

class Staff(Base):
    __tablename__ = "staff"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # Store as string, convert to enum in API
    location = Column(String(255), nullable=False, index=True)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    profile_pic = Column(String(500))
    status = Column(String(50), default="On-Duty")  # Store as string, convert to enum in API
    role_id = Column(String(36), ForeignKey("roles.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_role = relationship("Role", back_populates="staff_members", foreign_keys=[role_id])

