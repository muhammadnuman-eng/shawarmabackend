#!/usr/bin/env python3
"""
Test the complete forgot password flow
"""

import requests
import json
import sqlite3
import time

BASE_URL = "http://localhost:8000/api"

def get_latest_otp_from_db(email):
    """Get the latest OTP from database for testing"""
    try:
        # For PostgreSQL, we'd need different connection
        # For now, just return a dummy OTP for testing
        return "1234"  # This would be retrieved from actual DB in production
    except Exception as e:
        print(f"Database error: {e}")
        return None

def test_complete_forgot_password_flow():
    """Test the complete forgot password flow"""

    test_email = "akhaliq0153+2@gmail.com"

    print("=== Testing Complete Forgot Password Flow ===")
    print(f"Using email: {test_email}")
    print()

    # Step 1: Send forgot password request (should send OTP)
    print("Step 1: Sending forgot password request...")
    try:
        forgot_response = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": test_email})
        print(f"Status: {forgot_response.status_code}")

        if forgot_response.status_code == 200:
            response_data = forgot_response.json()
            print(f"Response: {response_data}")

            if response_data.get('otpSent'):
                print("✅ OTP sent successfully!")
            else:
                print("❌ OTP not sent")
                return
        else:
            print(f"❌ Request failed: {forgot_response.text}")
            return

    except Exception as e:
        print(f"❌ Network error: {e}")
        return

    print()

    # Step 2: Simulate OTP verification (in real app, user enters OTP)
    print("Step 2: Simulating OTP verification...")
    # In production, you'd get the actual OTP from email/database
    # For testing, we'll assume OTP verification succeeds

    print("✅ OTP verification simulated")

    print()

    # Step 3: Reset password with OTP
    print("Step 3: Resetting password with OTP...")
    try:
        reset_data = {
            "email": test_email,
            "otp": "1234",  # Dummy OTP for testing
            "password": "newpassword123",
            "confirmPassword": "newpassword123"
        }

        reset_response = requests.post(f"{BASE_URL}/auth/reset-password-with-otp", json=reset_data)
        print(f"Status: {reset_response.status_code}")

        if reset_response.status_code == 200:
            response_data = reset_response.json()
            print(f"Response: {response_data}")
            print("✅ Password reset successful!")
        else:
            print(f"❌ Password reset failed: {reset_response.text}")

    except Exception as e:
        print(f"❌ Network error: {e}")

    print()
    print("=== Flow Test Complete ===")

if __name__ == "__main__":
    test_complete_forgot_password_flow()













