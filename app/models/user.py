from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # For email/password auth
    avatar = Column(String(500), nullable=True)
    # provider = Column(String(50), nullable=True)  # 'google', 'facebook', etc. - TEMPORARILY COMMENTED OUT
    # provider_id = Column(String(255), nullable=True)  # OAuth provider user ID - TEMPORARILY COMMENTED OUT
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    loyalty_points = relationship("LoyaltyPoint", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    payment_cards = relationship("PaymentCard", back_populates="user", cascade="all, delete-orphan")
    chat_participants = relationship("ChatParticipant", back_populates="user", cascade="all, delete-orphan")

class OTP(Base):
    __tablename__ = "otps"

    id = Column(String(36), primary_key=True, index=True)
    phone_number = Column(String(20), nullable=True, index=True)  # Optional for email OTP
    email = Column(String(255), nullable=True, index=True)  # Optional for email OTP
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(50), nullable=False)  # 'login', 'register', 'reset_password'
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "Home", "Work"
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_default = Column(Boolean, default=False)
    type = Column(String(50), default="home")  # 'home', 'work', 'other'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="delivery_address")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    customizations = Column(Text)  # JSON string for customizations
    add_ons = Column(Text)  # JSON string for add-ons
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("MenuItem", foreign_keys=[product_id])

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    product = relationship("MenuItem", foreign_keys=[product_id], overlaps="favorites")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # 'order_status', 'promotion', 'review', etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text)  # JSON string for additional data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class NotificationSettings(Base):
    __tablename__ = "notification_settings"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    order_updates = Column(Boolean, default=True)
    promotions = Column(Boolean, default=True)
    new_products = Column(Boolean, default=True)
    reviews = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])

class LoyaltyPoint(Base):
    __tablename__ = "loyalty_points"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    points = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)  # 'earned', 'used', 'expired'
    description = Column(Text)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="loyalty_points")
    order = relationship("Order", foreign_keys=[order_id])

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    points_required = Column(Integer, nullable=False)
    image = Column(String(500))
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    query = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="search_history")

class PaymentCard(Base):
    __tablename__ = "payment_cards"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    card_number = Column(String(20), nullable=False)  # Last 4 digits only
    card_holder_name = Column(String(255), nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    card_type = Column(String(50))  # 'visa', 'mastercard', etc.
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payment_cards")

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(String(36), primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # 'direct', 'group'
    name = Column(String(255), nullable=True)  # For group chats
    description = Column(Text, nullable=True)  # For group chats
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    participants = relationship("ChatParticipant", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

class ChatParticipant(Base):
    __tablename__ = "chat_participants"
    
    id = Column(String(36), primary_key=True, index=True)
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # 'admin', 'member'
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat = relationship("Chat", back_populates="participants")
    user = relationship("User", back_populates="chat_participants")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String(36), primary_key=True, index=True)
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="text")  # 'text', 'image', 'file'
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])

class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(String(36), primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_type = Column(String(50), nullable=False)  # 'percentage', 'fixed'
    discount_value = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0.0)
    max_discount = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

