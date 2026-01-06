#!/usr/bin/env python3
"""
Check SMS configuration status
"""
import os
import sys
sys.path.append('.')

try:
    from app.core.config import settings
    from app.core.sms import sms_service

    print("SMS Configuration Check:")
    print("=" * 50)
    print(f"SMS_ENABLED: {settings.SMS_ENABLED}")
    print(f"SMS_PROVIDER: {settings.SMS_PROVIDER}")
    print(f"TWILIO_ACCOUNT_SID: {'Set' if settings.TWILIO_ACCOUNT_SID else 'Not Set'}")
    print(f"TWILIO_AUTH_TOKEN: {'Set' if settings.TWILIO_AUTH_TOKEN else 'Not Set'}")
    print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")
    print()

    print("SMS Service Provider:")
    print(f"Provider Type: {type(sms_service.provider).__name__}")
    print()

    # Test SMS service initialization
    print("Testing SMS Service:")
    print("Provider initialized successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
