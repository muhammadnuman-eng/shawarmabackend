#!/usr/bin/env python3
"""
Test script for reset password with OTP functionality
"""

import requests
import json
import sqlite3

BASE_URL = "http://localhost:8000/api"

def get_otp_from_db(email):
    """Get OTP from database for testing"""
    try:
        conn = sqlite3.connect("shawarma_local.db")
        cursor = conn.cursor()
        cursor.execute("SELECT otp_code FROM otps WHERE email = ? AND purpose = 'forgot_password' ORDER BY created_at DESC LIMIT 1", (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Database error: {e}")
        return None

def test_reset_password_with_otp():
    """Test the reset password with OTP flow"""

    # First, trigger forgot password to get OTP
    test_email = "akhaliq0153+2@gmail.com"

    print("Step 1: Sending forgot password request...")
    forgot_response = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": test_email})
    print(f"Status: {forgot_response.status_code}")
    print(f"Response: {forgot_response.json()}")

    if forgot_response.status_code != 200:
        print("Failed to send OTP")
        return

    # Get OTP from database (for testing only)
    print("\nStep 2: Getting OTP from database...")
    otp_code = get_otp_from_db(test_email)
    if not otp_code:
        print("No OTP found in database")
        return

    print(f"OTP: {otp_code}")

    # Now reset password with OTP
    print("\nStep 3: Resetting password with OTP...")
    reset_data = {
        "email": test_email,
        "otp": otp_code,
        "password": "newpassword123",
        "confirmPassword": "newpassword123"
    }

    reset_response = requests.post(f"{BASE_URL}/auth/reset-password-with-otp", json=reset_data)
    print(f"Status: {reset_response.status_code}")
    print(f"Response: {reset_response.json()}")

    if reset_response.status_code == 200:
        print("\n✅ Password reset with OTP successful!")
    else:
        print("\n❌ Password reset failed")

if __name__ == "__main__":
    print("Testing Reset Password with OTP Flow")
    print("=" * 40)
    test_reset_password_with_otp()













