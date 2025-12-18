from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from app.core.database import get_db
from app.models.review import Review
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
def create_review(review_data: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new review"""
    # Verify customer and order exist
    customer = db.query(Customer).filter(Customer.id == review_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if review_data.order_id:
        order = db.query(Order).filter(Order.id == review_data.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if review already exists for this order
        existing_review = db.query(Review).filter(Review.order_id == review_data.order_id).first()
        if existing_review:
            raise HTTPException(status_code=400, detail="Review already exists for this order")
        
        # Update order rating
        order.review_rating = review_data.rating
    
    # Update customer average rating
    customer_reviews = db.query(Review).filter(Review.customer_id == review_data.customer_id).all()
    all_ratings = [r.rating for r in customer_reviews] + [review_data.rating]
    customer.review_rating = sum(all_ratings) / len(all_ratings)
    
    review_id = str(uuid.uuid4())
    review = Review(
        id=review_id,
        **review_data.dict()
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return format_review_response(review, db)

@router.get("/", response_model=List[ReviewResponse])
def get_reviews(
    branch: Optional[str] = Query(None),
    rating: Optional[int] = Query(None, ge=1, le=5),
    customer_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all reviews with optional filters"""
    query = db.query(Review)
    
    if branch:
        query = query.filter(Review.branch == branch)
    if rating:
        query = query.filter(Review.rating == rating)
    if customer_id:
        query = query.filter(Review.customer_id == customer_id)
    if start_date:
        query = query.filter(Review.created_at >= start_date)
    if end_date:
        query = query.filter(Review.created_at <= end_date)
    
    reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    return [format_review_response(r, db) for r in reviews]

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: str, db: Session = Depends(get_db)):
    """Get review by ID"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return format_review_response(review, db)

def format_review_response(review: Review, db: Session) -> ReviewResponse:
    """Format review response with customer name"""
    customer = db.query(Customer).filter(Customer.id == review.customer_id).first()
    return ReviewResponse(
        id=review.id,
        order_id=review.order_id,
        customer_id=review.customer_id,
        customer_name=customer.name if customer else "Unknown",
        rating=review.rating,
        review_text=review.review_text,
        branch=review.branch,
        created_at=review.created_at
    )

