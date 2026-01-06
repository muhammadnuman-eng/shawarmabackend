#!/usr/bin/env python3
"""
Test script for email OTP registration flow
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_email_registration():
    """Test the complete email registration flow"""

    # Step 1: Register with email (should send OTP)
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }

    print("Step 1: Sending registration request...")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response text: {response.text}")
    if response.headers.get('content-type', '').startswith('application/json'):
        try:
            print(f"Response JSON: {response.json()}")
        except:
            print("Failed to parse JSON response")
    else:
        print("Response is not JSON")

    if response.status_code != 200:
        print("Registration failed!")
        return

    # Step 2: Check the mock email output (since email is disabled in dev)
    print("\nStep 2: Check mock email output above...")

    # For testing, we'll manually check the database for the OTP
    # In a real scenario, you'd get the OTP from email

    # Step 3: Get OTP from database (for testing only)
    print("\nStep 3: Getting OTP from database...")
    try:
        import sqlite3
        conn = sqlite3.connect("shawarma_local.db")
        cursor = conn.cursor()
        cursor.execute("SELECT otp_code FROM otps WHERE email = ? ORDER BY created_at DESC LIMIT 1", ("test@example.com",))
        result = cursor.fetchone()
        conn.close()

        if result:
            otp_code = result[0]
            print(f"OTP from database: {otp_code}")

            # Step 4: Verify OTP
            verify_data = {
                "email": "test@example.com",
                "otp": otp_code,
                "name": "Test User",
                "password": "testpassword123"
            }

            print("\nStep 4: Verifying OTP...")
            response = requests.post(f"{BASE_URL}/auth/verify-email-otp", json=verify_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

            if response.status_code == 200:
                print("\n✅ Email registration flow completed successfully!")
                token = response.json().get("token")
                print(f"JWT Token: {token[:50]}...")
            else:
                print("\n❌ OTP verification failed!")
        else:
            print("No OTP found in database!")

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    print("Testing Email OTP Registration Flow")
    print("=" * 40)
    test_email_registration()
