from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_user
from app.models.menu import Category, MenuItem
from app.models.user import User, Favorite
from app.models.review import Review
from math import ceil

router = APIRouter()

# Response Models
class CategoryResponse(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None
    image: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None
    category: str
    rating: float = 0.0
    reviewsCount: int = 0
    distance: Optional[str] = None
    deliveryTime: Optional[str] = None
    isAvailable: bool = True
    isFavorite: bool = False

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    
    return {
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "image": cat.image
            }
            for cat in categories
        ]
    }

@router.get("/products")
async def get_products(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get products by category with pagination"""
    query = db.query(MenuItem)
    
    if category:
        # Find category by name or id
        cat = db.query(Category).filter(
            or_(Category.id == category, Category.name.ilike(f"%{category}%"))
        ).first()
        if cat:
            query = query.filter(MenuItem.category_id == cat.id)
    
    # Filter available products
    query = query.filter(MenuItem.is_available == True)
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    # Get user favorites if authenticated
    favorite_ids = set()
    if current_user:
        favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
        favorite_ids = {fav.product_id for fav in favorites}
    
    products_list = []
    for product in products:
        # Calculate average rating
        reviews = db.query(Review).filter(Review.product_id == product.id).all()
        rating = 0.0
        if reviews:
            rating = sum(r.rating for r in reviews) / len(reviews)
        
        products_list.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image": product.image,
            "category": product.category.name if product.category else "",
            "rating": round(rating, 1),
            "reviewsCount": len(reviews),
            "distance": product.distance,
            "deliveryTime": product.delivery_time,
            "isAvailable": product.is_available,
            "isFavorite": product.id in favorite_ids
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

# Specific routes must come before parameterized routes to avoid conflicts
@router.get("/products/recommended")
async def get_recommended_products(
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get recommended products for user"""
    query = db.query(MenuItem).filter(MenuItem.is_available == True)

    if category:
        cat = db.query(Category).filter(
            or_(Category.id == category, Category.name.ilike(f"%{category}%"))
        ).first()
        if cat:
            query = query.filter(MenuItem.category_id == cat.id)

    # Get user's favorite categories or order history
    # For now, just return top rated products
    products = query.order_by(
        MenuItem.rating.desc(),
        MenuItem.order_count.desc()
    ).limit(limit).all()

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
            "distance": product.distance,
            "rating": round(rating, 1),
            "reviewsCount": len(reviews),
            "deliveryTime": product.delivery_time,
            "category": product.category.name if product.category else ""
        })

    return {"products": products_list}

@router.get("/products/{product_id}")
async def get_product_details(
    product_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get product details"""
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get reviews
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    rating = 0.0
    if reviews:
        rating = sum(r.rating for r in reviews) / len(reviews)
    
    # Check if favorite
    is_favorite = False
    if current_user:
        favorite = db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.product_id == product_id
        ).first()
        is_favorite = favorite is not None
    
    # Parse customization options and add-ons from JSON
    customization_options = product.customization_options or {}
    add_ons = product.optional_add_ons or []
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image": product.image,
        "images": product.images or [],
        "category": product.category.name if product.category else "",
        "rating": round(rating, 1),
        "reviewsCount": len(reviews),
        "distance": product.distance,
        "deliveryTime": product.delivery_time,
        "isAvailable": product.is_available,
        "isFavorite": is_favorite,
        "orderCount": product.order_count,
        "customizationOptions": customization_options,
        "addOns": [
            {
                "id": idx + 1,
                "name": addon.get("name", ""),
                "price": addon.get("price", 0.0),
                "image": addon.get("image")
            }
            for idx, addon in enumerate(add_ons)
        ] if isinstance(add_ons, list) else []
    }

@router.get("/products/high-demand")
async def get_high_demand_products(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get high-demand products (fastest near you)"""
    # Get products ordered by order count and rating
    products = db.query(MenuItem).filter(
        MenuItem.is_available == True
    ).order_by(
        MenuItem.order_count.desc(),
        MenuItem.rating.desc()
    ).limit(limit).all()
    
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
            "distance": product.distance
        })
    
    return {"products": products_list}

@router.get("/products/family-deals")
async def get_family_deals(db: Session = Depends(get_db)):
    """Get family deals"""
    # Get products that might be family deals (higher price, indicating combo)
    products = db.query(MenuItem).filter(
        MenuItem.is_available == True,
        MenuItem.price >= 2000  # Assuming family deals are higher priced
    ).order_by(MenuItem.price.desc()).limit(10).all()
    
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
            "description": product.description
        })
    
    return {"products": products_list}

