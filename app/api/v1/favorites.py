from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.user import User, Favorite
from app.models.menu import MenuItem
from app.models.review import Review

router = APIRouter()

# Request Models
class AddFavoriteRequest(BaseModel):
    productId: str

@router.get("/favorites")
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user favorites"""
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    
    favorites_list = []
    for fav in favorites:
        product = fav.product
        if not product:
            continue
        
        # Get rating
        reviews = db.query(Review).filter(Review.product_id == product.id).all()
        rating = 0.0
        if reviews:
            rating = sum(r.rating for r in reviews) / len(reviews)
        
        favorites_list.append({
            "id": product.id,
            "name": product.name,
            "image": product.image,
            "distance": product.distance,
            "rating": round(rating, 1),
            "reviews": str(len(reviews)),
            "price": product.price
        })
    
    return {"favorites": favorites_list}

@router.post("/favorites")
async def add_to_favorites(
    request: AddFavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add product to favorites"""
    # Check if product exists
    product = db.query(MenuItem).filter(MenuItem.id == request.productId).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already favorited
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == request.productId
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in favorites"
        )
    
    favorite = Favorite(
        id=generate_uuid(),
        user_id=current_user.id,
        product_id=request.productId
    )
    
    db.add(favorite)
    db.commit()
    
    return {
        "message": "Added to favorites successfully",
        "productId": request.productId
    }

@router.delete("/favorites/{product_id}")
async def remove_from_favorites(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove product from favorites"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == product_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    db.delete(favorite)
    db.commit()
    
    return {
        "message": "Removed from favorites successfully",
        "productId": product_id
    }

