#!/usr/bin/env python3
"""
Test script for forgot password functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_forgot_password():
    """Test the forgot password flow"""

    # Test with a non-existent email (should return success but not send email)
    test_email = "nonexistent@example.com"

    print("Testing forgot password with non-existent email...")
    forgot_data = {
        "email": test_email
    }

    response = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test with an existing user email
    # First, let's check if there's a user in the database
    try:
        import sqlite3
        conn = sqlite3.connect("shawarma_local.db")
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            existing_email = result[0]
            print(f"\nTesting forgot password with existing email: {existing_email}")

            forgot_data = {
                "email": existing_email
            }

            response = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        else:
            print("No users found in database")

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    print("Testing Forgot Password Flow")
    print("=" * 30)
    test_forgot_password()













