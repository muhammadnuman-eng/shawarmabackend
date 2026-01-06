#!/usr/bin/env python3
"""
Test OTP registration flow
"""
import asyncio
import sys
import os
sys.path.append('.')

async def test_otp_flow():
    """Test the complete OTP flow"""
    try:
        from app.core.sms import sms_service
        from app.core.database import get_db
        from app.models.user import OTP
        from app.core.security import generate_otp
        from sqlalchemy.orm import Session
        from datetime import datetime, timedelta

        print("Testing OTP Flow...")
        print("=" * 50)

        # Test SMS service initialization
        print("1. SMS Service Status:")
        print(f"   Provider: {type(sms_service.provider).__name__}")
        print(f"   Initialized: {'✅' if sms_service.provider else '❌'}")
        print()

        # Test OTP generation
        print("2. Testing OTP Generation:")
        test_phone = "+923124368343"
        otp_code = generate_otp()
        print(f"   Phone: {test_phone}")
        print(f"   Generated OTP: {otp_code}")
        print()

        # Test SMS sending
        print("3. Testing SMS Sending:")
        sms_result = await sms_service.send_otp(test_phone, otp_code)
        print(f"   SMS Result: {'✅ Success' if sms_result else '❌ Failed'}")
        print()

        # Test database operations
        print("4. Testing Database Operations:")
        db = next(get_db())
        try:
            # Clean up any existing OTPs for this phone
            db.query(OTP).filter(OTP.phone_number == test_phone).delete()
            db.commit()

            # Create test OTP
            test_otp = OTP(
                id=f"test-{otp_code}",
                phone_number=test_phone,
                otp_code=otp_code,
                purpose="register",
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            db.add(test_otp)
            db.commit()

            # Verify OTP was saved
            saved_otp = db.query(OTP).filter(OTP.phone_number == test_phone).first()
            if saved_otp:
                print("   ✅ OTP saved to database")
                print(f"   📝 Saved OTP: {saved_otp.otp_code}")
            else:
                print("   ❌ OTP not found in database")

        except Exception as e:
            print(f"   ❌ Database error: {e}")
        finally:
            db.close()

        print()
        print("=" * 50)
        print("OTP Flow Test Complete!")
        print()
        print("Next steps:")
        print("1. Start the backend server: python run.py")
        print("2. Test phone registration from the mobile app")
        print("3. Use the OTP shown in console to complete registration")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_otp_flow())
