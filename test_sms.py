#!/usr/bin/env python3
"""
Test SMS service to debug OTP issues
"""
import asyncio
import os
import sys

# Add current directory to path
sys.path.append('.')

from app.core.sms import sms_service

async def test_sms():
    """Test SMS service functionality"""
    print("Testing SMS Service...")
    print("=" * 50)

    # Initialize provider
    sms_service._initialize_provider()

    # Test phone number (use your actual phone number for testing)
    test_phone = "+923001234567"  # Replace with actual phone number

    print(f"\nTesting OTP send to: {test_phone}")
    print("Check the console output above for SMS service status")
    print("If you see 'MOCK SMS', then real SMS is not configured")

    # Try sending OTP
    success = await sms_service.send_otp(test_phone, "123456")

    if success:
        print("✅ OTP send function returned success")
        print("Check your phone for SMS or look for OTP in console output")
    else:
        print("❌ OTP send function failed")
        print("Check backend logs for detailed error")

    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_sms())
