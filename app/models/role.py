from sqlalchemy import Column, String, DateTime, ForeignKey, Table, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Association table for many-to-many relationship
role_permission_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permission_table, back_populates="roles")
    staff_members = relationship("Staff", back_populates="assigned_role")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    label = Column(String(255), nullable=False)
    category = Column(String(100))  # e.g., "orders", "menu", "staff", "finance"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=role_permission_table, back_populates="permissions")

