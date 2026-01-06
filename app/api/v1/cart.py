from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.user import CartItem, User
from app.models.user import PromoCode
from app.models.menu import MenuItem
import json

router = APIRouter()

# Request Models
class AddToCartRequest(BaseModel):
    productId: str
    quantity: int = 1
    customizations: Optional[Dict] = None
    addOns: Optional[List[Dict]] = None

class UpdateCartItemRequest(BaseModel):
    quantity: int

class ApplyPromoRequest(BaseModel):
    promoCode: str

# Constants for fees
DELIVERY_FEE = 100.0
PLATFORM_FEE = 8.0
GST_RATE = 0.18  # 18% GST

def calculate_cart_totals(cart_items: List[CartItem], promo_discount: float = 0.0) -> Dict:
    """Calculate cart totals"""
    subtotal = 0.0
    
    for item in cart_items:
        product = item.product
        if product:
            item_total = product.price * item.quantity
            
            # Add add-ons price if any
            if item.add_ons:
                try:
                    add_ons_data = json.loads(item.add_ons) if isinstance(item.add_ons, str) else item.add_ons
                    if isinstance(add_ons_data, list):
                        for addon in add_ons_data:
                            item_total += addon.get("price", 0.0) * addon.get("quantity", 1)
                except:
                    pass
            
            subtotal += item_total
    
    delivery_fee = DELIVERY_FEE
    platform_fee = PLATFORM_FEE
    gst = (subtotal + delivery_fee + platform_fee - promo_discount) * GST_RATE
    total = subtotal + delivery_fee + platform_fee + gst - promo_discount
    
    return {
        "subtotal": round(subtotal, 2),
        "deliveryFee": round(delivery_fee, 2),
        "platformFee": round(platform_fee, 2),
        "gst": round(gst, 2),
        "total": round(total, 2),
        "promoDiscount": round(promo_discount, 2)
    }

@router.get("/cart")
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's cart"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    # Get applied promo code
    promo_discount = 0.0
    # In a real app, you'd store the applied promo in session or user preferences
    
    totals = calculate_cart_totals(cart_items, promo_discount)
    
    items_list = []
    for item in cart_items:
        product = item.product
        if not product:
            continue
        
        customizations = {}
        if item.customizations:
            try:
                customizations = json.loads(item.customizations) if isinstance(item.customizations, str) else item.customizations
            except:
                pass
        
        add_ons = []
        if item.add_ons:
            try:
                add_ons_data = json.loads(item.add_ons) if isinstance(item.add_ons, str) else item.add_ons
                if isinstance(add_ons_data, list):
                    add_ons = add_ons_data
            except:
                pass
        
        items_list.append({
            "id": item.id,
            "productId": item.product_id,
            "productName": product.name,
            "price": product.price,
            "quantity": item.quantity,
            "image": product.image,
            "customizations": customizations,
            "addOns": add_ons
        })
    
    return {
        "items": items_list,
        **totals
    }

@router.post("/cart")
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    # Check if product exists
    product = db.query(MenuItem).filter(MenuItem.id == request.productId).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not product.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available"
        )
    
    # Check if item already exists in cart with same customizations
    # For simplicity, we'll create a new item each time
    # In production, you might want to merge items with same customizations
    
    cart_item = CartItem(
        id=generate_uuid(),
        user_id=current_user.id,
        product_id=request.productId,
        quantity=request.quantity,
        customizations=json.dumps(request.customizations) if request.customizations else None,
        add_ons=json.dumps(request.addOns) if request.addOns else None
    )
    
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    
    # Get add-ons details
    add_ons_list = []
    if request.addOns:
        for addon in request.addOns:
            add_ons_list.append({
                "id": addon.get("id", 0),
                "name": addon.get("name", ""),
                "price": addon.get("price", 0.0),
                "quantity": addon.get("quantity", 1)
            })
    
    return {
        "id": cart_item.id,
        "productId": cart_item.product_id,
        "productName": product.name,
        "price": product.price,
        "quantity": cart_item.quantity,
        "image": product.image,
        "customizations": request.customizations or {},
        "addOns": add_ons_list
    }

@router.put("/cart/{cart_item_id}")
async def update_cart_item(
    cart_item_id: str,
    request: UpdateCartItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    if request.quantity <= 0:
        # Remove item if quantity is 0 or less
        db.delete(cart_item)
        db.commit()
        return {"message": "Item removed from cart"}
    
    cart_item.quantity = request.quantity
    db.commit()
    db.refresh(cart_item)
    
    product = cart_item.product
    total = product.price * cart_item.quantity if product else 0.0
    
    return {
        "id": cart_item.id,
        "quantity": cart_item.quantity,
        "price": product.price if product else 0.0,
        "total": total
    }

@router.delete("/cart/{cart_item_id}")
async def remove_cart_item(
    cart_item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart successfully"}

@router.delete("/cart")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear entire cart"""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "Cart cleared successfully"}

@router.post("/cart/promo")
async def apply_promo_code(
    request: ApplyPromoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply promo code"""
    promo = db.query(PromoCode).filter(
        PromoCode.code == request.promoCode.upper(),
        PromoCode.is_active == True
    ).first()
    
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired promo code"
        )
    
    # Check expiry
    from datetime import datetime
    if promo.expires_at and promo.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired promo code"
        )
    
    # Check usage limit
    if promo.usage_limit and promo.used_count >= promo.usage_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired promo code"
        )
    
    # Get cart total
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    totals = calculate_cart_totals(cart_items, 0.0)
    
    # Calculate discount
    if promo.discount_type == "percentage":
        discount = totals["subtotal"] * (promo.discount_value / 100)
        if promo.max_discount:
            discount = min(discount, promo.max_discount)
    else:
        discount = promo.discount_value
    
    # Check min order amount
    if totals["subtotal"] < promo.min_order_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum order amount of {promo.min_order_amount} required"
        )
    
    return {
        "promoCode": promo.code,
        "discount": round(discount, 2),
        "discountType": promo.discount_type,
        "discountValue": promo.discount_value,
        "message": "Promo code applied successfully"
    }

