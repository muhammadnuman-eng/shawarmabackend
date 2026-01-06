#!/usr/bin/env python3
"""
Force SMS service initialization and check status
"""
import sys
sys.path.append('.')

from app.core.sms import sms_service

print("Forcing SMS Service Initialization...")
print("=" * 50)

# Force initialization
sms_service._initialize_provider()

print("SMS Service Status:")
print(f"Provider: {type(sms_service.provider).__name__}")
print(f"SMS_ENABLED: {sms_service.provider is not None}")

if hasattr(sms_service, 'provider') and sms_service.provider:
    if hasattr(sms_service.provider, 'client'):
        print("Twilio client initialized")
    else:
        print("Using mock provider")

print("=" * 50)
