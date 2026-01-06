#!/usr/bin/env python3
import os

print('Environment Variables:')
print(f'TWILIO_ACCOUNT_SID: {os.getenv("TWILIO_ACCOUNT_SID", "Not set")}')
print(f'TWILIO_AUTH_TOKEN: {os.getenv("TWILIO_AUTH_TOKEN", "Not set")}')
print(f'TWILIO_PHONE_NUMBER: {os.getenv("TWILIO_PHONE_NUMBER", "Not set")}')
print(f'SMS_ENABLED: {os.getenv("SMS_ENABLED", "Not set")}')

# Also check if twilio package is installed
try:
    import twilio
    print(f'Twilio package: Installed (version {twilio.__version__})')
except ImportError:
    print('Twilio package: Not installed')
