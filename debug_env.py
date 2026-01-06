#!/usr/bin/env python3
"""
Debug environment variables and settings loading
"""
import os
import sys
sys.path.append('.')

from app.core.config import settings

print("Environment Variables Check:")
print("=" * 50)
print(f"TWILIO_ACCOUNT_SID: {os.getenv('TWILIO_ACCOUNT_SID', 'NOT SET')}")
print(f"TWILIO_AUTH_TOKEN: {os.getenv('TWILIO_AUTH_TOKEN', 'NOT SET')}")
print(f"TWILIO_PHONE_NUMBER: {os.getenv('TWILIO_PHONE_NUMBER', 'NOT SET')}")
print(f"SMS_ENABLED: {os.getenv('SMS_ENABLED', 'NOT SET')}")
print(f"SMS_PROVIDER: {os.getenv('SMS_PROVIDER', 'NOT SET')}")

print("\nPydantic Settings Check:")
print("=" * 50)
print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
print(f"TWILIO_AUTH_TOKEN: {settings.TWILIO_AUTH_TOKEN}")
print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")
print(f"SMS_ENABLED: {settings.SMS_ENABLED}")
print(f"SMS_PROVIDER: {settings.SMS_PROVIDER}")

print("\nCurrent Working Directory:")
print(f"CWD: {os.getcwd()}")

print("\nChecking for .env files:")
import glob
env_files = glob.glob("**/.env", recursive=True)
for env_file in env_files:
    print(f"Found: {env_file}")

print("=" * 50)
