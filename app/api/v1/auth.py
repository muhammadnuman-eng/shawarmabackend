from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    generate_otp, generate_uuid
)
from app.models.user import User, OTP
from app.core.auth import get_current_user

router = APIRouter()
security = HTTPBearer()

# Request/Response Models
class EmailLoginRequest(BaseModel):
    email: str
    password: str

class EmailRegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class PhoneLoginRequest(BaseModel):
    phoneNumber: str

class PhoneRegisterRequest(BaseModel):
    phoneNumber: str

class VerifyOTPRequest(BaseModel):
    phoneNumber: str
    otp: str

class ResendOTPRequest(BaseModel):
    phoneNumber: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    token: str
    password: str
    confirmPassword: str

class GoogleLoginRequest(BaseModel):
    idToken: str
    accessToken: str

class FacebookLoginRequest(BaseModel):
    accessToken: str

class UserResponse(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    avatar: Optional[str] = None
    isOnline: bool
    # Aapka lastSeen response mein ISO format mein hai, isliye str
    lastSeen: Optional[str] = None 
    isAdmin: bool
    
    # Pydantic ko allow karein ke woh SQLAlchemy objects se yeh data read kar sake
    class Config:
        from_attributes = True # Ya 'orm_mode = True' agar aapka pydantic purana hai

class AuthResponse(BaseModel):
    token: str
    user: UserResponse
    isNewUser: Optional[bool] = None

class OTPResponse(BaseModel):
    message: str
    otpSent: bool
    phoneNumber: str

# Helper Functions
def create_user_response(user: User) -> dict:
    """Create user response dict"""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phoneNumber": user.phone_number,
        "avatar": user.avatar,
        "isOnline": user.is_online,
        "lastSeen": user.last_seen.isoformat() if user.last_seen else None,
        "isAdmin": user.is_admin
    }

# Authentication Endpoints
@router.post("/login", response_model=AuthResponse)
async def email_login(request: EmailLoginRequest, db: Session = Depends(get_db)):
    """Email login endpoint"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update user online status
    user.is_online = True
    user.last_seen = datetime.utcnow()
    db.commit()
    
    # Create token
    token = create_access_token(data={"sub": user.id})
    
    return {
        "token": token,
        "user": create_user_response(user)
    }

@router.post("/register", response_model=AuthResponse)
async def email_register(request: EmailRegisterRequest, db: Session = Depends(get_db)):
    """Email registration endpoint"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    user = User(
        id=generate_uuid(),
        name=request.name,
        email=request.email,
        password_hash=get_password_hash(request.password),
        is_online=True,
        last_seen=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create token
    token = create_access_token(data={"sub": user.id})
    
    return {
        "token": token,
        "user": create_user_response(user)
    }

@router.post("/phone/login", response_model=OTPResponse)
async def phone_login(request: PhoneLoginRequest, db: Session = Depends(get_db)):
    """Phone login - send OTP"""
    # Validate phone number format (basic validation)
    if not request.phoneNumber.startswith("+") or len(request.phoneNumber) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number"
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Store or update OTP
    existing_otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.purpose == "login"
    ).first()
    
    if existing_otp:
        existing_otp.otp_code = otp_code
        existing_otp.expires_at = expires_at
        existing_otp.is_verified = False
    else:
        otp = OTP(
            id=generate_uuid(),
            phone_number=request.phoneNumber,
            otp_code=otp_code,
            purpose="login",
            expires_at=expires_at
        )
        db.add(otp)
    
    db.commit()
    
    # In production, send OTP via SMS service
    # For now, we'll just return success
    print(f"OTP for {request.phoneNumber}: {otp_code}")  # Remove in production
    
    return {
        "message": "OTP sent successfully",
        "otpSent": True,
        "phoneNumber": request.phoneNumber
    }

@router.post("/phone/register", response_model=OTPResponse)
async def phone_register(request: PhoneRegisterRequest, db: Session = Depends(get_db)):
    """Phone registration - send OTP"""
    # Validate phone number format
    if not request.phoneNumber.startswith("+") or len(request.phoneNumber) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number"
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Store or update OTP
    existing_otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.purpose == "register"
    ).first()
    
    if existing_otp:
        existing_otp.otp_code = otp_code
        existing_otp.expires_at = expires_at
        existing_otp.is_verified = False
    else:
        otp = OTP(
            id=generate_uuid(),
            phone_number=request.phoneNumber,
            otp_code=otp_code,
            purpose="register",
            expires_at=expires_at
        )
        db.add(otp)
    
    db.commit()
    
    # In production, send OTP via SMS service
    print(f"OTP for {request.phoneNumber}: {otp_code}")  # Remove in production
    
    return {
        "message": "OTP sent successfully",
        "otpSent": True,
        "phoneNumber": request.phoneNumber
    }

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and login/register"""
    # Find OTP
    otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.otp_code == request.otp,
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as verified
    otp.is_verified = True
    
    # Check if user exists
    user = db.query(User).filter(User.phone_number == request.phoneNumber).first()
    is_new_user = False
    
    if not user:
        # Create new user
        is_new_user = True
        user = User(
            id=generate_uuid(),
            phone_number=request.phoneNumber,
            is_online=True,
            last_seen=datetime.utcnow()
        )
        db.add(user)
    else:
        # Update existing user
        user.is_online = True
        user.last_seen = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Create token
    token = create_access_token(data={"sub": user.id})
    
    return {
        "token": token,
        "user": create_user_response(user),
        "isNewUser": is_new_user
    }

@router.post("/resend-otp", response_model=dict)
async def resend_otp(request: ResendOTPRequest, db: Session = Depends(get_db)):
    """Resend OTP"""
    # Find existing OTP
    existing_otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber
    ).order_by(OTP.created_at.desc()).first()
    
    if not existing_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP request found"
        )
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    existing_otp.otp_code = otp_code
    existing_otp.expires_at = expires_at
    existing_otp.is_verified = False
    
    db.commit()
    
    # In production, send OTP via SMS service
    print(f"Resent OTP for {request.phoneNumber}: {otp_code}")  # Remove in production
    
    return {
        "message": "OTP resent successfully",
        "otpSent": True
    }

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset link/OTP"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Don't reveal if email exists for security
        return {"message": "Password reset link sent to your email"}
    
    # In production, send reset link via email
    # For now, we'll just return success
    return {"message": "Password reset link sent to your email"}

@router.post("/reset-password", response_model=dict)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password"""
    if request.password != request.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # In production, verify reset token from email
    # For now, we'll just update the password
    user.password_hash = get_password_hash(request.password)
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.post("/google", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Google social login"""
    # In production, verify Google token
    # For now, this is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google login not implemented yet"
    )

@router.post("/facebook", response_model=AuthResponse)
async def facebook_login(request: FacebookLoginRequest, db: Session = Depends(get_db)):
    """Facebook social login"""
    # In production, verify Facebook token
    # For now, this is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Facebook login not implemented yet"
    )

@router.post("/logout", response_model=dict)
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout endpoint"""
    current_user.is_online = False
    current_user.last_seen = datetime.utcnow()
    db.commit()
    
    return {"message": "Logged out successfully"}

