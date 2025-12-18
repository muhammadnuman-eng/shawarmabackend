from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel
from math import ceil
from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_user
from app.core.security import generate_uuid
from app.models.review import Review
from app.models.user import User
from app.models.menu import MenuItem

router = APIRouter()

# Request Models
class AddReviewRequest(BaseModel):
    rating: int  # 1-5
    comment: Optional[str] = None
    images: Optional[List[str]] = None

class UpdateReviewRequest(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    images: Optional[List[str]] = None

@router.get("/products/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    rating: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """Get product reviews"""
    # Verify product exists
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    query = db.query(Review).filter(Review.product_id == product_id)
    
    if rating:
        query = query.filter(Review.rating == rating)
    
    total = query.count()
    offset = (page - 1) * limit
    reviews = query.order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
    
    reviews_list = []
    for review in reviews:
        user = review.user
        customer = review.customer
        
        reviews_list.append({
            "id": review.id,
            "userId": review.user_id or review.customer_id,
            "userName": user.name if user else (customer.name if customer else "Anonymous"),
            "userAvatar": user.avatar if user else (customer.profile_pic if customer else None),
            "rating": review.rating,
            "comment": review.comment or review.review_text,
            "images": review.images or [],
            "createdAt": review.created_at.isoformat() if review.created_at else None,
            "helpful": review.helpful_count
        })
    
    # Calculate summary
    all_reviews = db.query(Review).filter(Review.product_id == product_id).all()
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_rating = 0
    
    for rev in all_reviews:
        rating_distribution[rev.rating] = rating_distribution.get(rev.rating, 0) + 1
        total_rating += rev.rating
    
    average_rating = total_rating / len(all_reviews) if all_reviews else 0.0
    
    return {
        "reviews": reviews_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": ceil(total / limit) if total > 0 else 0
        },
        "summary": {
            "averageRating": round(average_rating, 1),
            "totalReviews": len(all_reviews),
            "ratingDistribution": {
                "5": rating_distribution[5],
                "4": rating_distribution[4],
                "3": rating_distribution[3],
                "2": rating_distribution[2],
                "1": rating_distribution[1]
            }
        }
    }

@router.post("/products/{product_id}/reviews")
async def add_review(
    product_id: str,
    request: AddReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add product review"""
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Verify product exists
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed this product
    existing_review = db.query(Review).filter(
        Review.product_id == product_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    review = Review(
        id=generate_uuid(),
        product_id=product_id,
        user_id=current_user.id,
        rating=request.rating,
        comment=request.comment,
        images=request.images
    )
    
    db.add(review)
    
    # Update product rating
    all_reviews = db.query(Review).filter(Review.product_id == product_id).all()
    if all_reviews:
        product.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        product.reviews_count = len(all_reviews)
    
    db.commit()
    db.refresh(review)
    
    return {
        "id": review.id,
        "userId": review.user_id,
        "userName": current_user.name,
        "userAvatar": current_user.avatar,
        "rating": review.rating,
        "comment": review.comment,
        "images": review.images or [],
        "createdAt": review.created_at.isoformat() if review.created_at else None
    }

@router.put("/reviews/{review_id}")
async def update_review(
    review_id: str,
    request: UpdateReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if request.rating is not None:
        if request.rating < 1 or request.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        review.rating = request.rating
    
    if request.comment is not None:
        review.comment = request.comment
    
    if request.images is not None:
        review.images = request.images
    
    db.commit()
    db.refresh(review)
    
    # Update product rating
    if review.product_id:
        product = db.query(MenuItem).filter(MenuItem.id == review.product_id).first()
        if product:
            all_reviews = db.query(Review).filter(Review.product_id == review.product_id).all()
            if all_reviews:
                product.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    
    db.commit()
    
    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "images": review.images or [],
        "updatedAt": review.updated_at.isoformat() if review.updated_at else None
    }

@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    product_id = review.product_id
    db.delete(review)
    
    # Update product rating
    if product_id:
        product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
        if product:
            all_reviews = db.query(Review).filter(Review.product_id == product_id).all()
            if all_reviews:
                product.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
                product.reviews_count = len(all_reviews)
            else:
                product.rating = 0.0
                product.reviews_count = 0
    
    db.commit()
    
    return {"message": "Review deleted successfully"}

