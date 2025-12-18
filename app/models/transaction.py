from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TransactionStatus(str, enum.Enum):
    COMPLETED = "Completed"
    REFUND = "Refund"
    PENDING = "Pending"

class PaymentMethod(str, enum.Enum):
    CASH = "Cash"
    CARD_VISA = "Card (VISA)"
    CARD_MASTER = "Card (Master)"
    BANK_TRANSFER_MEEZAN = "Meezan Bank Transfer"
    BANK_TRANSFER_ALLIED = "Allied Bank Transfer"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), unique=True, nullable=True)  # Made nullable for mobile app
    amount = Column(Float, nullable=False)
    payment_method = Column(String(100), nullable=False)  # Changed to String for flexibility
    status = Column(String(50), default="pending")  # Changed to String: 'pending', 'success', 'failed', 'refunded'
    transaction_id = Column(String(100), nullable=True)  # External transaction ID
    branch = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="transaction")

