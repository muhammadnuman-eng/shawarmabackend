#!/usr/bin/env python3
"""
Test script for email service directly
"""

import asyncio
import logging
from app.core.email import email_service
from app.core.config import settings

# Enable logging to see more details
logging.basicConfig(level=logging.INFO)

async def test_email_service():
    """Test the email service directly"""

    print("Testing email service initialization...")
    print(f"EMAIL_ENABLED: {getattr(settings, 'EMAIL_ENABLED', False)}")
    print(f"EMAIL_PROVIDER: {getattr(settings, 'EMAIL_PROVIDER', 'not set')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'not set')}")
    print(f"EMAIL_USER: {getattr(settings, 'EMAIL_USER', 'not set')}")
    print(f"EMAIL_PASS: {'*' * len(getattr(settings, 'EMAIL_PASS', '')) if getattr(settings, 'EMAIL_PASS', None) else 'not set'}")

    # Check if email service is initialized
    print(f"\nEmail provider: {type(email_service.provider).__name__}")

    # Try to send a test email
    print("\nSending test email...")
    try:
        success = await email_service.send_password_reset_email(
            to_email="akhaliq0153+2@gmail.com",  # Use the existing user email
            reset_token="test-token-123",
            reset_link="https://yourapp.com/reset-password?token=test-token-123&email=akhaliq0153+2@gmail.com"
        )

        print(f"Email sent: {success}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    print("Testing Email Service Directly")
    print("=" * 30)
    asyncio.run(test_email_service())
