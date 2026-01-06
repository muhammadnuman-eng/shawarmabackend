from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ItemStatus(str, enum.Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(500), nullable=True)
    image = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    image = Column(String(500))  # Main image
    images = Column(JSON)  # Array of image URLs
    status = Column(String(50), default="Available")
    is_available = Column(Boolean, default=True)
    main_components = Column(JSON)  # Array of {name: str, price?: float}
    spicy_elements = Column(JSON)  # Array of strings
    additional_flavor = Column(JSON)  # Array of {name: str, price: float}
    optional_add_ons = Column(JSON)  # Array of {name: str, price: float}
    customization_options = Column(JSON)  # For breadType, filling, sides, sauces, spiceLevel
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)
    distance = Column(String(50), nullable=True)  # e.g., "1.5 km"
    delivery_time = Column(String(50), nullable=True)  # e.g., "30-40 min"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    section_items = relationship("MenuSectionItem", back_populates="menu_item")
    favorites = relationship("Favorite", foreign_keys="Favorite.product_id")
    reviews = relationship("Review", foreign_keys="Review.product_id")

class MenuSection(Base):
    __tablename__ = "menu_sections"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    items = relationship("MenuSectionItem", back_populates="section", cascade="all, delete-orphan")

class MenuSectionItem(Base):
    __tablename__ = "menu_section_items"
    
    id = Column(String(36), primary_key=True, index=True)
    section_id = Column(String(36), ForeignKey("menu_sections.id"), nullable=False)
    menu_item_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    section = relationship("MenuSection", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="section_items")

