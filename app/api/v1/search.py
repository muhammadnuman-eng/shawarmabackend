from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_user
from app.models.menu import MenuItem, Category
from app.models.user import User, SearchHistory, Favorite
from app.models.review import Review
from math import ceil

router = APIRouter()

@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Search products"""
    query = db.query(MenuItem).filter(
        MenuItem.is_available == True,
        or_(
            MenuItem.name.ilike(f"%{q}%"),
            MenuItem.description.ilike(f"%{q}%")
        )
    )
    
    if category:
        cat = db.query(Category).filter(
            or_(Category.id == category, Category.name.ilike(f"%{category}%"))
        ).first()
        if cat:
            query = query.filter(MenuItem.category_id == cat.id)
    
    total = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    # Get user favorites if authenticated
    favorite_ids = set()
    if current_user:
        favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
        favorite_ids = {fav.product_id for fav in favorites}
    
    products_list = []
    for product in products:
        reviews = db.query(Review).filter(Review.product_id == product.id).all()
        rating = 0.0
        if reviews:
            rating = sum(r.rating for r in reviews) / len(reviews)
        
        products_list.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image": product.image,
            "rating": round(rating, 1),
            "reviewsCount": len(reviews),
            "category": product.category.name if product.category else ""
        })
    
    return {
        "products": products_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": ceil(total / limit) if total > 0 else 0
        }
    }

@router.get("/search/recent")
async def get_recent_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent searches"""
    searches = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(SearchHistory.created_at.desc()).limit(10).all()
    
    # Get unique queries
    unique_queries = []
    seen = set()
    for search in searches:
        if search.query not in seen:
            unique_queries.append(search.query)
            seen.add(search.query)
    
    return {"searches": unique_queries[:10]}

@router.get("/search/popular")
async def get_popular_searches(db: Session = Depends(get_db)):
    """Get popular searches"""
    # Get most searched queries
    popular = db.query(
        SearchHistory.query,
        func.count(SearchHistory.id).label('count')
    ).group_by(SearchHistory.query).order_by(
        func.count(SearchHistory.id).desc()
    ).limit(10).all()
    
    return {
        "searches": [item[0] for item in popular]
    }

@router.post("/search/history")
async def save_search_history(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save search history"""
    from app.core.security import generate_uuid
    
    search_history = SearchHistory(
        id=generate_uuid(),
        user_id=current_user.id,
        query=query
    )
    db.add(search_history)
    db.commit()
    
    return {"message": "Search saved successfully"}

