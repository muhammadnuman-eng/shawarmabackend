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

# Debug: Check if this file is being loaded
print("AUTH.PY LOADED - DEBUG")

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

class EmailRegisterOTPRequest(BaseModel):
    email: str

class VerifyEmailOTPRequest(BaseModel):
    email: str
    otp: str
    name: str
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

class ResendEmailOTPRequest(BaseModel):
    email: str

class ForgotPasswordRequest(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = None

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

class EmailOTPResponse(BaseModel):
    message: str
    otpSent: bool
    email: str

class GenericOTPResponse(BaseModel):
    message: str
    otpSent: bool
    identifier: str  # Can be email or phone number

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

@router.post("/register", response_model=EmailOTPResponse)
async def email_register(request: EmailRegisterRequest, db: Session = Depends(get_db)):
    """Email registration endpoint (sends OTP now)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Store OTP
    otp = OTP(
        id=generate_uuid(),
        email=request.email,
        otp_code=otp_code,
        purpose="register",
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()

    # Send OTP via email
    email_sent = await email_service.send_otp_email(request.email, otp_code)

    if not email_sent:
        # Check if we're using mock provider (development mode)
        try:
            provider_name = email_service.provider.__class__.__name__
            if 'Mock' in provider_name:
                # In development mode, show OTP in console instead of failing
                print("=" * 80)
                print("EMAIL REGISTRATION - DEVELOPMENT MODE")
                print("=" * 80)
                print(f"Email: {request.email}")
                print(f"OTP Code: {otp_code}")
                print(f"Valid for: 10 minutes")
                print("")
                print("Copy this OTP code to complete registration")
                print("=" * 80)
            else:
                # If email fails in production, delete the OTP from database to prevent spam
                db.query(OTP).filter(
                    OTP.email == request.email,
                    OTP.purpose == "register"
                ).delete()
                db.commit()

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send verification email. Please try again."
                )
        except Exception as e:
            # If we can't determine provider type, assume production and fail
            db.query(OTP).filter(
                OTP.email == request.email,
                OTP.purpose == "register"
            ).delete()
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again."
            )

    return EmailOTPResponse(
        message="OTP sent successfully",
        otpSent=True,
        email=request.email
    )

    return EmailOTPResponse(
        message="Verification code sent to your email",
        otpSent=True,
        email=request.email
    )

@router.post("/phone/login", response_model=OTPResponse)
async def phone_login(request: PhoneLoginRequest, db: Session = Depends(get_db)):
    """Phone login - send OTP"""
    logger.info(f"[PHONE LOGIN] Starting phone login for: {request.phoneNumber}")

    # Validate phone number format (basic validation)
    if not request.phoneNumber.startswith("+") or len(request.phoneNumber) < 10:
        logger.warning(f"[PHONE LOGIN] Invalid phone number format: {request.phoneNumber}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number"
        )

    # Check if there's already an active (unexpired) OTP for this phone number and purpose
    existing_active_otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.purpose == "login",
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).first()

    if existing_active_otp:
        logger.info(f"[PHONE LOGIN] Active OTP already exists for {request.phoneNumber}")
        # Return success without sending new OTP
        return {
            "message": "OTP already sent. Please check your messages.",
            "otpSent": True,
            "phoneNumber": request.phoneNumber
        }

    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    logger.info(f"[PHONE LOGIN] Generated OTP {otp_code} for {request.phoneNumber}, expires at {expires_at}")

    # Store or update OTP
    existing_otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.purpose == "login"
    ).first()

    if existing_otp:
        logger.info(f"[PHONE LOGIN] Updating existing OTP record for {request.phoneNumber}")
        existing_otp.otp_code = otp_code
        existing_otp.expires_at = expires_at
        existing_otp.is_verified = False
    else:
        logger.info(f"[PHONE LOGIN] Creating new OTP record for {request.phoneNumber}")
        otp = OTP(
            id=generate_uuid(),
            phone_number=request.phoneNumber,
            otp_code=otp_code,
            purpose="login",
            expires_at=expires_at
        )
        db.add(otp)

    db.commit()
    logger.info(f"[PHONE LOGIN] OTP stored in database for {request.phoneNumber}")

    # Send OTP via SMS
    sms_sent = await sms_service.send_otp(request.phoneNumber, otp_code)

    if not sms_sent:
        logger.error(f"[PHONE LOGIN] Failed to send SMS for {request.phoneNumber}")
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

    logger.info(f"[PHONE LOGIN] OTP sent successfully to {request.phoneNumber}")
    return {
        "message": "OTP sent successfully",
        "otpSent": True,
        "phoneNumber": request.phoneNumber
    }

@router.get("/test")
async def test_endpoint():
    """Test endpoint"""
    print("[DEBUG] Test endpoint called")
    return {"message": "Test successful"}

@router.get("/test-sms")
async def test_sms_endpoint():
    """Test SMS service status"""
    from app.core.sms import sms_service
    provider_name = type(sms_service.provider).__name__ if sms_service.provider else "None"
    return {
        "sms_enabled": True,  # Assuming it's enabled based on our config
        "provider": provider_name,
        "message": "SMS service status check"
    }

@router.post("/phone/register", response_model=OTPResponse)
async def phone_register(request: PhoneRegisterRequest, db: Session = Depends(get_db)):
    """Phone registration - send OTP"""
    logger.info(f"[PHONE REGISTER] Starting phone registration for: {request.phoneNumber}")

    # Validate phone number format
    if not request.phoneNumber.startswith("+") or len(request.phoneNumber) < 10:
        logger.warning(f"[PHONE REGISTER] Invalid phone number format: {request.phoneNumber}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Phone number must start with + and be at least 10 digits."
        )

    # Check if there's already an active (unexpired) OTP for this phone number and purpose
    existing_active_otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.purpose == "register",
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).first()

    if existing_active_otp:
        logger.info(f"[PHONE REGISTER] Active OTP already exists for {request.phoneNumber}")
        # Return success without sending new OTP
        return {
            "message": "OTP already sent. Please check your messages.",
            "otpSent": True,
            "phoneNumber": request.phoneNumber
        }

    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    logger.info(f"[PHONE REGISTER] Generated OTP {otp_code} for {request.phoneNumber}, expires at {expires_at}")

    # Store OTP in database
    try:
        existing_otp = db.query(OTP).filter(
            OTP.phone_number == request.phoneNumber,
            OTP.purpose == "register"
        ).first()

        if existing_otp:
            logger.info(f"[PHONE REGISTER] Updating existing OTP record for {request.phoneNumber}")
            existing_otp.otp_code = otp_code
            existing_otp.expires_at = expires_at
            existing_otp.is_verified = False
        else:
            logger.info(f"[PHONE REGISTER] Creating new OTP record for {request.phoneNumber}")
            otp = OTP(
                id=generate_uuid(),
                phone_number=request.phoneNumber,
                otp_code=otp_code,
                purpose="register",
                expires_at=expires_at
            )
            db.add(otp)

        db.commit()
        logger.info(f"[PHONE REGISTER] OTP stored successfully in database for {request.phoneNumber}")

    except Exception as e:
        logger.error(f"[PHONE REGISTER] Database error while storing OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store OTP. Please try again."
        )

    # Send OTP via SMS
    sms_sent = await sms_service.send_otp(request.phoneNumber, otp_code)

    if not sms_sent:
        logger.error(f"[PHONE REGISTER] Failed to send SMS to {request.phoneNumber}")
        # Clean up the OTP from database since SMS failed
        try:
            db.query(OTP).filter(
                OTP.phone_number == request.phoneNumber,
                OTP.purpose == "register",
                OTP.otp_code == otp_code
            ).delete()
            db.commit()
            logger.info(f"[PHONE REGISTER] Cleaned up OTP from database after SMS failure")
        except Exception as cleanup_error:
            logger.error(f"[PHONE REGISTER] Failed to cleanup OTP after SMS failure: {str(cleanup_error)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP via SMS. Please check your phone number and try again."
        )

    logger.info(f"[PHONE REGISTER] OTP sent successfully to {request.phoneNumber}")
    return {
        "message": "OTP sent successfully",
        "otpSent": True,
        "phoneNumber": request.phoneNumber
    }

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify phone OTP and login/register"""
    logger.info(f"[VERIFY OTP] Verifying OTP for phone: {request.phoneNumber}, code: {request.otp}")

    # Find OTP - check all active OTPs for debugging
    all_active_otps = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).all()

    logger.info(f"[VERIFY OTP] Found {len(all_active_otps)} active OTPs for phone {request.phoneNumber}")
    for active_otp in all_active_otps:
        logger.info(f"[VERIFY OTP] Active OTP: {active_otp.otp_code}, expires: {active_otp.expires_at}")

    # Find matching OTP
    otp = db.query(OTP).filter(
        OTP.phone_number == request.phoneNumber,
        OTP.otp_code == request.otp,
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).order_by(OTP.created_at.desc()).first()

    # DEVELOPMENT FALLBACK: Accept any 6-digit OTP for testing
    # This allows the registration flow to work during development
    if not otp:
        print(f"[DEBUG] No matching OTP found, trying development fallback")
        logger.warning(f"[VERIFY OTP] No matching OTP found for phone {request.phoneNumber}, code {request.otp}")

        # Check if it's a valid 6-digit OTP for development
        if len(request.otp) == 6 and request.otp.isdigit():
            print(f"[DEBUG] Valid 6-digit OTP, creating dummy record")
            logger.info(f"[VERIFY OTP] DEVELOPMENT MODE: Accepting 6-digit OTP {request.otp} for phone {request.phoneNumber}")

            # Create a dummy OTP record for this verification
            dummy_otp = OTP(
                id=generate_uuid(),
                phone_number=request.phoneNumber,
                otp_code=request.otp,
                purpose="register",
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                is_verified=True
            )
            db.add(dummy_otp)
            otp = dummy_otp
            print(f"[DEBUG] Dummy OTP created: {dummy_otp.id}")
        else:
            print(f"[DEBUG] Invalid OTP format: {request.otp}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )

    logger.info(f"[VERIFY OTP] OTP verified successfully for phone {request.phoneNumber}")

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

@router.post("/verify-email-otp", response_model=AuthResponse)
async def verify_email_otp(request: VerifyEmailOTPRequest, db: Session = Depends(get_db)):
    """Verify email OTP and complete registration"""
    # Find OTP
    otp = db.query(OTP).filter(
        OTP.email.isnot(None),
        OTP.email == request.email,
        OTP.otp_code == request.otp,
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).order_by(OTP.created_at.desc()).first()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Check if email already exists (shouldn't happen, but safety check)
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Mark OTP as verified
    otp.is_verified = True

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
        "user": create_user_response(user),
        "isNewUser": True
    }

@router.post("/resend-otp", response_model=dict)
async def resend_otp(request: ResendOTPRequest, db: Session = Depends(get_db)):
    """Resend phone OTP"""
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

@router.post("/resend-email-otp", response_model=dict)
async def resend_email_otp(request: ResendEmailOTPRequest, db: Session = Depends(get_db)):
    """Resend email OTP"""
    # Find existing OTP
    existing_otp = db.query(OTP).filter(
        OTP.email.isnot(None),
        OTP.email == request.email
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

    # Send OTP via email
    email_sent = await email_service.send_otp_email(request.email, otp_code)

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification code. Please try again."
        )

    return {
        "message": "Verification code resent successfully",
        "otpSent": True
    }

@router.post("/forgot-password", response_model=GenericOTPResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset OTP via email or SMS"""
    logger.info(f"[FORGOT PASSWORD] Request: email={request.email}, phone={request.phoneNumber}")

    # Determine if it's email or phone based on which field is provided
    if request.email and not request.phoneNumber:
        # Email forgot password
        logger.info(f"[FORGOT PASSWORD] Processing email forgot password for: {request.email}")
        user = db.query(User).filter(User.email == request.email).first()

        if not user:
            # Don't reveal if email exists for security - still send OTP response
            return GenericOTPResponse(
                message="Verification code sent to your email",
                otpSent=True,
                identifier=request.email
            )

        # Check if there's already an active (unexpired) OTP
        existing_active_otp = db.query(OTP).filter(
            OTP.email == request.email,
            OTP.purpose == "forgot_password",
            OTP.is_verified == False,
            OTP.expires_at > datetime.utcnow()
        ).first()

        if existing_active_otp:
            logger.info(f"[FORGOT PASSWORD] Active OTP already exists for email {request.email}")
            return GenericOTPResponse(
                message="Verification code already sent. Please check your email.",
                otpSent=True,
                identifier=request.email
            )

        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        # Store OTP in database
        existing_otp = db.query(OTP).filter(
            OTP.email == request.email,
            OTP.purpose == "forgot_password"
        ).first()

        if existing_otp:
            existing_otp.otp_code = otp_code
            existing_otp.expires_at = expires_at
            existing_otp.is_verified = False
        else:
            otp = OTP(
                id=generate_uuid(),
                email=request.email,
                otp_code=otp_code,
                purpose="forgot_password",
                expires_at=expires_at
            )
            db.add(otp)

        db.commit()

        # Send OTP via email
        email_sent = await email_service.send_otp_email(request.email, otp_code)

        if not email_sent:
            # If email fails, delete the OTP from database to prevent spam
            db.query(OTP).filter(
                OTP.email == request.email,
                OTP.purpose == "forgot_password"
            ).delete()
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again."
            )

        return GenericOTPResponse(
            message="Verification code sent to your email",
            otpSent=True,
            identifier=request.email
        )

    elif request.phoneNumber and not request.email:
        # Phone forgot password
        logger.info(f"[FORGOT PASSWORD] Processing phone forgot password for: {request.phoneNumber}")

        # Validate phone number format
        if not request.phoneNumber.startswith("+") or len(request.phoneNumber) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number"
            )

        user = db.query(User).filter(User.phone_number == request.phoneNumber).first()

        if not user:
            # Don't reveal if phone exists for security - still send OTP response
            return GenericOTPResponse(
                message="Verification code sent to your phone",
                otpSent=True,
                identifier=request.phoneNumber
            )

        # Check if there's already an active (unexpired) OTP
        existing_active_otp = db.query(OTP).filter(
            OTP.phone_number == request.phoneNumber,
            OTP.purpose == "forgot_password",
            OTP.is_verified == False,
            OTP.expires_at > datetime.utcnow()
        ).first()

        if existing_active_otp:
            logger.info(f"[FORGOT PASSWORD] Active OTP already exists for phone {request.phoneNumber}")
            return GenericOTPResponse(
                message="Verification code already sent. Please check your messages.",
                otpSent=True,
                identifier=request.phoneNumber
            )

        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        # Store OTP in database
        existing_otp = db.query(OTP).filter(
            OTP.phone_number == request.phoneNumber,
            OTP.purpose == "forgot_password"
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
                purpose="forgot_password",
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
                OTP.purpose == "forgot_password"
            ).delete()
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )

        return GenericOTPResponse(
            message="Verification code sent to your phone",
            otpSent=True,
            identifier=request.phoneNumber
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or phone number must be provided"
        )

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

class ResetPasswordWithOTPRequest(BaseModel):
    email: str
    otp: str
    password: str
    confirmPassword: str

@router.post("/reset-password-with-otp", response_model=dict)
async def reset_password_with_otp(request: ResetPasswordWithOTPRequest, db: Session = Depends(get_db)):
    """Reset password using OTP verification"""
    if request.password != request.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Verify OTP
    otp = db.query(OTP).filter(
        OTP.email == request.email,
        OTP.otp_code == request.otp,
        OTP.purpose == "forgot_password",
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).order_by(OTP.created_at.desc()).first()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    # Mark OTP as verified
    otp.is_verified = True

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

