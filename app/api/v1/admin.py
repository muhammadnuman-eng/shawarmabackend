from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from math import ceil
from app.core.database import get_db
from app.core.auth import get_current_admin_user
from app.models.user import User
from app.models.order import Order
from app.models.menu import MenuItem

router = APIRouter()

# Request Models
class MakeAdminRequest(BaseModel):
    userId: str

# Global settings (in production, store in database)
registration_enabled = True

@router.get("/admin/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    
    # Calculate total revenue
    total_revenue = db.query(func.sum(Order.total)).scalar() or 0.0
    
    # Active orders (pending, confirmed, preparing, ready, out_for_delivery)
    active_orders = db.query(Order).filter(
        Order.status.in_(["pending", "confirmed", "preparing", "ready", "out_for_delivery"])
    ).count()
    
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    
    return {
        "totalUsers": total_users,
        "totalOrders": total_orders,
        "totalRevenue": total_revenue,
        "activeOrders": active_orders,
        "pendingOrders": pending_orders,
        "registrationEnabled": registration_enabled
    }

@router.get("/admin/users")
async def get_all_users_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            func.or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    offset = (page - 1) * limit
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    users_list = []
    for user in users:
        # Get user order stats
        orders = db.query(Order).filter(Order.user_id == user.id).all()
        total_orders = len(orders)
        total_spent = sum(order.total for order in orders)
        
        users_list.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phoneNumber": user.phone_number,
            "avatar": user.avatar,
            "isAdmin": user.is_admin,
            "isOnline": user.is_online,
            "lastSeen": user.last_seen.isoformat() if user.last_seen else None,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
            "totalOrders": total_orders,
            "totalSpent": total_spent
        })
    
    return {
        "users": users_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": ceil(total / limit) if total > 0 else 0
        }
    }

@router.post("/admin/registration/enable")
async def enable_registration(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Enable user registration"""
    global registration_enabled
    registration_enabled = True
    
    return {
        "message": "Registration enabled successfully",
        "registrationEnabled": True
    }

@router.post("/admin/registration/disable")
async def disable_registration(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Disable user registration"""
    global registration_enabled
    registration_enabled = False
    
    return {
        "message": "Registration disabled successfully",
        "registrationEnabled": False
    }

@router.delete("/admin/users/{user_id}")
async def delete_user_admin(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.post("/admin/users")
async def make_user_admin(
    request: MakeAdminRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Make user admin"""
    user = db.query(User).filter(User.id == request.userId).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = True
    db.commit()
    
    return {
        "message": "User promoted to admin successfully",
        "userId": request.userId
    }

