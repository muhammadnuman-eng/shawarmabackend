from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from math import ceil
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.user import User, Notification, NotificationSettings

router = APIRouter()

# Request Models
class UpdateNotificationSettingsRequest(BaseModel):
    orderUpdates: Optional[bool] = None
    promotions: Optional[bool] = None
    newProducts: Optional[bool] = None
    reviews: Optional[bool] = None
    pushNotifications: Optional[bool] = None
    emailNotifications: Optional[bool] = None

@router.get("/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unreadOnly: Optional[bool] = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unreadOnly:
        query = query.filter(Notification.is_read == False)
    
    total = query.count()
    offset = (page - 1) * limit
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    # Count unread
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    notifications_list = []
    for notif in notifications:
        data = {}
        if notif.data:
            try:
                import json
                data = json.loads(notif.data) if isinstance(notif.data, str) else notif.data
            except:
                pass
        
        notifications_list.append({
            "id": notif.id,
            "type": notif.type,
            "title": notif.title,
            "message": notif.message,
            "data": data,
            "isRead": notif.is_read,
            "createdAt": notif.created_at.isoformat() if notif.created_at else None
        })
    
    return {
        "notifications": notifications_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": ceil(total / limit) if total > 0 else 0
        },
        "unreadCount": unread_count
    }

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return {
        "message": "Notification marked as read",
        "notificationId": notification_id
    }

@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {
        "message": "All notifications marked as read",
        "count": count
    }

@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted successfully"}

@router.get("/notifications/settings")
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification settings"""
    settings = db.query(NotificationSettings).filter(
        NotificationSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings
        settings = NotificationSettings(
            id=generate_uuid(),
            user_id=current_user.id
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "orderUpdates": settings.order_updates,
        "promotions": settings.promotions,
        "newProducts": settings.new_products,
        "reviews": settings.reviews,
        "pushNotifications": settings.push_notifications,
        "emailNotifications": settings.email_notifications
    }

@router.put("/notifications/settings")
async def update_notification_settings(
    request: UpdateNotificationSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification settings"""
    settings = db.query(NotificationSettings).filter(
        NotificationSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = NotificationSettings(
            id=generate_uuid(),
            user_id=current_user.id
        )
        db.add(settings)
    
    if request.orderUpdates is not None:
        settings.order_updates = request.orderUpdates
    if request.promotions is not None:
        settings.promotions = request.promotions
    if request.newProducts is not None:
        settings.new_products = request.newProducts
    if request.reviews is not None:
        settings.reviews = request.reviews
    if request.pushNotifications is not None:
        settings.push_notifications = request.pushNotifications
    if request.emailNotifications is not None:
        settings.email_notifications = request.emailNotifications
    
    db.commit()
    db.refresh(settings)
    
    return {
        "orderUpdates": settings.order_updates,
        "promotions": settings.promotions,
        "newProducts": settings.new_products,
        "reviews": settings.reviews,
        "pushNotifications": settings.push_notifications,
        "emailNotifications": settings.email_notifications,
        "message": "Settings updated successfully"
    }

