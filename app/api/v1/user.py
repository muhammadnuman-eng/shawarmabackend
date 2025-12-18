from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import verify_password, get_password_hash, generate_uuid
from app.models.user import User
from datetime import datetime

router = APIRouter()

# Request/Response Models
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str
    confirmPassword: str

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user profile"""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phoneNumber": current_user.phone_number,
        "avatar": current_user.avatar,
        "isOnline": current_user.is_online,
        "lastSeen": current_user.last_seen.isoformat() if current_user.last_seen else None,
        "isAdmin": current_user.is_admin,
        "createdAt": current_user.created_at.isoformat() if current_user.created_at else None,
        "updatedAt": current_user.updated_at.isoformat() if current_user.updated_at else None
    }

@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Check if email is being changed and if it's already taken
    if request.email and request.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == request.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        current_user.email = request.email
    
    # Check if phone number is being changed and if it's already taken
    if request.phoneNumber and request.phoneNumber != current_user.phone_number:
        existing_user = db.query(User).filter(
            User.phone_number == request.phoneNumber,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists"
            )
        current_user.phone_number = request.phoneNumber
    
    if request.name is not None:
        current_user.name = request.name
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phoneNumber": current_user.phone_number,
        "avatar": current_user.avatar,
        "isOnline": current_user.is_online,
        "lastSeen": current_user.last_seen.isoformat() if current_user.last_seen else None,
        "isAdmin": current_user.is_admin
    }

@router.post("/profile/avatar", response_model=dict)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    # In production, upload to cloud storage (S3, Cloudinary, etc.)
    # For now, we'll just return a placeholder URL
    # You should implement actual file upload logic here
    
    # Example: Save file and get URL
    # file_url = await save_file_to_storage(avatar, f"avatars/{current_user.id}")
    
    # For now, using a placeholder
    file_url = f"https://example.com/uploads/avatar_{current_user.id}.jpg"
    
    current_user.avatar = file_url
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "avatar": file_url,
        "message": "Profile picture updated successfully"
    }

@router.post("/change-password", response_model=dict)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password"""
    if request.newPassword != request.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password not set for this account"
        )
    
    if not verify_password(request.currentPassword, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.password_hash = get_password_hash(request.newPassword)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

