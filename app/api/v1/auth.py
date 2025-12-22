from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import logging
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    generate_otp, generate_uuid
)
from app.core.sms import sms_service
from app.core.email import email_service
from app.core.oauth import oauth_service
from app.models.user import User, OTP
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)

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
    provider: Optional[str] = None  # OAuth provider
    providerId: Optional[str] = None  # OAuth provider ID

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
        "isAdmin": user.is_admin,
        # "provider": user.provider,  # TEMPORARILY COMMENTED OUT
        # "providerId": user.provider_id  # TEMPORARILY COMMENTED OUT
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

    # Send welcome email (don't fail registration if email fails)
    try:
        await email_service.send_welcome_email(
            to_email=user.email,
            user_name=user.name or "there"
        )
    except Exception as e:
        logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")

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

    # Send OTP via SMS
    sms_sent = await sms_service.send_otp(request.phoneNumber, otp_code)

    if not sms_sent:
        # If SMS fails, delete the OTP from database to prevent spam
        db.query(OTP).filter(
            OTP.phone_number == request.phoneNumber,
            OTP.purpose == "login"
        ).delete()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )

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

    # Send OTP via SMS
    sms_sent = await sms_service.send_otp(request.phoneNumber, otp_code)

    if not sms_sent:
        # If SMS fails, delete the OTP from database to prevent spam
        db.query(OTP).filter(
            OTP.phone_number == request.phoneNumber,
            OTP.purpose == "register"
        ).delete()
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )

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

    # Send OTP via SMS
    sms_sent = await sms_service.send_otp(request.phoneNumber, otp_code)

    if not sms_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend OTP. Please try again."
        )

    return {
        "message": "OTP resent successfully",
        "otpSent": True
    }

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset link via email"""
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        # Don't reveal if email exists for security
        return {"message": "Password reset link sent to your email"}

    # Generate reset token (in production, use JWT or secure token)
    reset_token = generate_uuid()
    expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry

    # Store reset token in database (you might want to create a separate table for this)
    # For now, we'll use a simple approach
    user.password_hash = f"RESET_TOKEN:{reset_token}:{expires_at.timestamp()}"
    db.commit()

    # Generate reset link (adjust domain for production)
    reset_link = f"https://yourapp.com/reset-password?token={reset_token}&email={request.email}"

    # Send password reset email
    email_sent = await email_service.send_password_reset_email(
        to_email=request.email,
        reset_token=reset_token,
        reset_link=reset_link
    )

    if not email_sent:
        # If email fails, clean up the reset token
        user.password_hash = None  # Reset to original (this is not ideal, better to use separate field)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email. Please try again."
        )

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
            detail="Invalid reset request"
        )

    # Verify reset token
    if not user.password_hash or not user.password_hash.startswith("RESET_TOKEN:"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    try:
        _, token, expiry_timestamp = user.password_hash.split(":", 2)
        expiry_time = datetime.fromtimestamp(float(expiry_timestamp))

        if token != request.token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        if datetime.utcnow() > expiry_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )

    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token format"
        )

    # Update password
    user.password_hash = get_password_hash(request.password)
    db.commit()

    return {"message": "Password reset successfully"}

@router.post("/google", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Google OAuth login"""
    # Verify Google token
    user_info = await oauth_service.verify_google_token(request.idToken)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )

    # Check if user exists by email (provider_id check commented out)
    user = db.query(User).filter(
        User.email == user_info['email']
        # or_(User.provider_id == user_info['sub'])  # TEMPORARILY COMMENTED OUT
    ).first()

    is_new_user = False

    if not user:
        # Create new user
        user = User(
            id=generate_uuid(),
            name=user_info['name'],
            email=user_info['email'],
            avatar=user_info['picture'],
            # provider='google',  # TEMPORARILY COMMENTED OUT
            # provider_id=user_info['sub'],  # TEMPORARILY COMMENTED OUT
            is_online=True,
            last_seen=datetime.utcnow()
        )
        db.add(user)
        is_new_user = True

        # Send welcome email (don't fail if email fails)
        try:
            await email_service.send_welcome_email(
                to_email=user.email,
                user_name=user.name or "there"
            )
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")

    else:
        # Update existing user info
        user.name = user_info['name'] or user.name
        user.avatar = user_info['picture'] or user.avatar
        user.provider = 'google'
        user.provider_id = user_info['sub']
        user.is_online = True
        user.last_seen = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # Create JWT token
    token = create_access_token(data={"sub": user.id})

    return {
        "token": token,
        "user": create_user_response(user),
        "isNewUser": is_new_user
    }

@router.post("/facebook", response_model=AuthResponse)
async def facebook_login(request: FacebookLoginRequest, db: Session = Depends(get_db)):
    """Facebook OAuth login"""
    # Verify Facebook token
    user_info = await oauth_service.verify_facebook_token(request.accessToken)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Facebook token"
        )

    # Check if user exists by email (provider_id check commented out)
    user = db.query(User).filter(
        User.email == user_info['email'] if user_info['email'] else None
        # or_(User.provider_id == user_info['sub'])  # TEMPORARILY COMMENTED OUT
    ).first()

    is_new_user = False

    if not user:
        # Create new user
        user = User(
            id=generate_uuid(),
            name=user_info['name'],
            email=user_info['email'],
            avatar=user_info['picture'],
            # provider='facebook',  # TEMPORARILY COMMENTED OUT
            # provider_id=user_info['sub'],  # TEMPORARILY COMMENTED OUT
            is_online=True,
            last_seen=datetime.utcnow()
        )
        db.add(user)
        is_new_user = True

        # Send welcome email (don't fail if email fails)
        try:
            if user.email:
                await email_service.send_welcome_email(
                    to_email=user.email,
                    user_name=user.name or "there"
                )
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")

    else:
        # Update existing user info
        user.name = user_info['name'] or user.name
        user.avatar = user_info['picture'] or user.avatar
        # user.provider = 'facebook'  # TEMPORARILY COMMENTED OUT
        # user.provider_id = user_info['sub']  # TEMPORARILY COMMENTED OUT
        user.is_online = True
        user.last_seen = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # Create JWT token
    token = create_access_token(data={"sub": user.id})

    return {
        "token": token,
        "user": create_user_response(user),
        "isNewUser": is_new_user
    }

@router.post("/logout", response_model=dict)
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout endpoint"""
    current_user.is_online = False
    current_user.last_seen = datetime.utcnow()
    db.commit()
    
    return {"message": "Logged out successfully"}

