from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from app.core.database import get_db
from app.models.transaction import Transaction, TransactionStatus, PaymentMethod
from app.models.order import Order
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction_data: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction"""
    # Verify order exists
    order = db.query(Order).filter(Order.id == transaction_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        **transaction_data.dict()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return format_transaction_response(transaction, db)

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    status: Optional[TransactionStatus] = Query(None),
    payment_method: Optional[PaymentMethod] = Query(None),
    branch: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all transactions with optional filters"""
    query = db.query(Transaction)
    
    if status:
        query = query.filter(Transaction.status == status)
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method)
    if branch:
        query = query.filter(Transaction.branch == branch)
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    
    transactions = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return [format_transaction_response(t, db) for t in transactions]

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get transaction by ID"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return format_transaction_response(transaction, db)

def format_transaction_response(transaction: Transaction, db: Session) -> TransactionResponse:
    """Format transaction response with order number"""
    order = db.query(Order).filter(Order.id == transaction.order_id).first()
    return TransactionResponse(
        id=transaction.id,
        order_id=transaction.order_id,
        order_number=order.order_number if order else "N/A",
        amount=transaction.amount,
        payment_method=transaction.payment_method,
        status=transaction.status,
        branch=transaction.branch,
        created_at=transaction.created_at
    )

