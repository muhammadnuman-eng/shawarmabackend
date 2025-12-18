from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.user import User, PaymentCard
from app.models.order import Order

router = APIRouter()

# Request Models
class AddCardRequest(BaseModel):
    cardNumber: str
    cardHolderName: str
    expiryMonth: int
    expiryYear: int
    cvv: str
    isDefault: bool = False

class ProcessPaymentRequest(BaseModel):
    orderId: str
    paymentMethod: str
    cardId: Optional[str] = None
    amount: float

@router.get("/payment/methods")
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available payment methods"""
    return {
        "methods": [
            {
                "id": "cash",
                "name": "Cash on Delivery",
                "description": "Pay easily using Card, Easypaisa, JazzCash, or Cash on Delivery.",
                "icon": "cash",
                "isAvailable": True
            },
            {
                "id": "card",
                "name": "Credit or Debit Card",
                "description": "Use your card for secure payments.",
                "icon": "card",
                "isAvailable": True
            },
            {
                "id": "easypaisa",
                "name": "Easypaisa",
                "description": "Pay using Easypaisa wallet",
                "icon": "easypaisa",
                "isAvailable": True
            },
            {
                "id": "jazzcash",
                "name": "JazzCash",
                "description": "Pay using JazzCash wallet",
                "icon": "jazzcash",
                "isAvailable": True
            }
        ]
    }

@router.get("/payment/cards")
async def get_saved_cards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get saved payment cards"""
    cards = db.query(PaymentCard).filter(PaymentCard.user_id == current_user.id).all()
    
    return {
        "cards": [
            {
                "id": card.id,
                "cardNumber": card.card_number,
                "cardHolderName": card.card_holder_name,
                "expiryMonth": card.expiry_month,
                "expiryYear": card.expiry_year,
                "cardType": card.card_type,
                "isDefault": card.is_default
            }
            for card in cards
        ]
    }

@router.post("/payment/cards")
async def add_payment_card(
    request: AddCardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add payment card"""
    # Validate card number (basic validation)
    card_number_clean = request.cardNumber.replace(" ", "").replace("-", "")
    if len(card_number_clean) < 13 or len(card_number_clean) > 19:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid card number"
        )
    
    # Determine card type
    card_type = "visa"  # Default, in production use proper detection
    if card_number_clean.startswith("5"):
        card_type = "mastercard"
    elif card_number_clean.startswith("4"):
        card_type = "visa"
    
    # Mask card number (show only last 4 digits)
    masked_number = f"**** **** **** {card_number_clean[-4:]}"
    
    # If setting as default, unset other defaults
    if request.isDefault:
        db.query(PaymentCard).filter(
            PaymentCard.user_id == current_user.id,
            PaymentCard.is_default == True
        ).update({"is_default": False})
    
    card = PaymentCard(
        id=generate_uuid(),
        user_id=current_user.id,
        card_number=masked_number,
        card_holder_name=request.cardHolderName,
        expiry_month=request.expiryMonth,
        expiry_year=request.expiryYear,
        card_type=card_type,
        is_default=request.isDefault
    )
    
    db.add(card)
    db.commit()
    db.refresh(card)
    
    return {
        "id": card.id,
        "cardNumber": card.card_number,
        "cardHolderName": card.card_holder_name,
        "expiryMonth": card.expiry_month,
        "expiryYear": card.expiry_year,
        "cardType": card.card_type,
        "isDefault": card.is_default,
        "message": "Card added successfully"
    }

@router.delete("/payment/cards/{card_id}")
async def delete_payment_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete payment card"""
    card = db.query(PaymentCard).filter(
        PaymentCard.id == card_id,
        PaymentCard.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    db.delete(card)
    db.commit()
    
    return {"message": "Card deleted successfully"}

@router.post("/payment/process")
async def process_payment(
    request: ProcessPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payment"""
    # Verify order
    order = db.query(Order).filter(
        Order.id == request.orderId,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.payment_status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid"
        )
    
    # In production, integrate with payment gateway
    # For now, simulate payment processing
    
    if request.paymentMethod == "cash":
        # Cash on delivery - mark as pending
        order.payment_status = "pending"
        payment_status = "success"
    else:
        # Card/Online payment - simulate processing
        # In production, call payment gateway API
        order.payment_status = "paid"
        payment_status = "success"
    
    # Create transaction record
    from app.models.transaction import Transaction
    transaction = Transaction(
        id=generate_uuid(),
        order_id=order.id,
        amount=request.amount,
        payment_method=request.paymentMethod,
        status=payment_status,
        transaction_id=f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(transaction)
    
    return {
        "paymentId": transaction.id,
        "orderId": order.id,
        "status": payment_status,
        "amount": request.amount,
        "paymentMethod": request.paymentMethod,
        "transactionId": transaction.transaction_id,
        "paidAt": transaction.created_at.isoformat() if transaction.created_at else None
    }

