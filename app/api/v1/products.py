from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from typing import Optional, List
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_user
from app.models.menu import Category, MenuItem
from app.models.user import User, Favorite
from app.models.review import Review
from app.models.order import Order, OrderItem
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

# Categories endpoint moved to separate router

@router.get("/test")
def test_endpoint():
    """Test endpoint"""
    print("TEST ENDPOINT CALLED")
    return {"message": "Test endpoint working"}

# Specific routes must come before parameterized routes to avoid conflicts
@router.get("/recommended")
def get_recommended_products(
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get recommended products for user"""
    try:
        print(f"[Recommended API] Starting request: user={current_user.id if current_user else None}, category={category}, limit={limit}")

        base_query = db.query(MenuItem).filter(MenuItem.is_available == True)

        if category:
            cat = db.query(Category).filter(
                or_(Category.id == category, Category.name.ilike(f"%{category}%"))
            ).first()
            if cat:
                base_query = base_query.filter(MenuItem.category_id == cat.id)

        # Get products ordered by rating and order count (simplified approach)
        products = base_query.order_by(
            MenuItem.rating.desc(),
            MenuItem.order_count.desc(),
            MenuItem.price.desc()
        ).limit(limit).all()

        print(f"[Recommended API] Found {len(products)} products")

        # Format response
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
                "category": product.category.name if product.category else "",
                "recommendationReason": "Popular choice"
            })

        print(f"[Recommended API] Returning {len(products_list)} products")
        return {"products": products_list}

    except Exception as e:
        print(f"[Recommended API] Error: {e}")
        import traceback
        traceback.print_exc()
        # Return empty array on error to prevent crashes
        return {"products": []}

@router.get("/high-demand")
def get_high_demand_products(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get high-demand products (fastest near you)"""
    try:
        print(f"[High-Demand API] Starting with limit={limit}")

        # Simple approach: Get products with high order counts
        # This matches the high-demand logic but simplified
        products = db.query(MenuItem).filter(
            MenuItem.is_available == True,
            MenuItem.order_count > 0  # Only products that have been ordered
        ).order_by(
            MenuItem.order_count.desc(),  # Sort by order count (demand)
            MenuItem.rating.desc()
        ).limit(limit).all()

        print(f"[High-Demand API] Found {len(products)} products with orders")

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
                "distance": product.distance,
                "deliveryTime": product.delivery_time,
                "isAvailable": product.is_available
            })

        print(f"[High-Demand API] Returning {len(products_list)} products")
        return {"products": products_list}

    except Exception as e:
        print(f"[High-Demand API] Error: {e}")
        import traceback
        traceback.print_exc()
        # Return empty array on error
        return {"products": []}

@router.get("/family-deals")
def get_family_deals(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get family deals - combo meals, family packs, and value deals"""
    try:
        print(f"[Family Deals API] Starting with limit={limit}")

        # Simple approach: Get all products with price >= 2500
        # This matches the frontend filter logic
        products = db.query(MenuItem).filter(
            MenuItem.is_available == True,
            MenuItem.price >= 2500
        ).order_by(
            MenuItem.price.desc(),
            MenuItem.rating.desc()
        ).limit(limit).all()

        print(f"[Family Deals API] Found {len(products)} products with price >= 2500")

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
                "description": product.description,
                "distance": product.distance,
                "deliveryTime": product.delivery_time,
                "isAvailable": product.is_available
            })

        print(f"[Family Deals API] Returning {len(products_list)} products")
        return {"products": products_list}

    except Exception as e:
        print(f"[Family Deals API] Error: {e}")
        import traceback
        traceback.print_exc()
        # Return empty array on error
        return {"products": []}

@router.get("/")
def get_products(
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
        # Calculate average rating from reviews, or use stored rating
        reviews = db.query(Review).filter(Review.product_id == product.id).all()
        rating = float(product.rating or 0.0)  # Use stored rating as default, ensure it's float
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
            "reviewsCount": len(reviews) if reviews else product.reviews_count,
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

@router.get("/{product_id}")
def get_product_details(
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

