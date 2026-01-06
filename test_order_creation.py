#!/usr/bin/env python3
import requests
import json

def test_order_creation_without_address():
    print("=== Order Creation Test (Without Address) ===\n")

    # First login
    print("1. Logging in...")
    login_response = requests.post('http://localhost:8000/api/auth/login',
                                   json={'email': 'test@example.com', 'password': 'password123'})

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        return

    login_data = login_response.json()
    token = login_data['token']
    print("Login successful!")

    # Now create order WITHOUT address
    print("\n2. Creating order without address...")
    order_data = {
        "items": [{
            "productId": "prod_001",
            "quantity": 1,
            "price": 250.0,
            "customizations": None,
            "addOns": None
        }],
        "deliveryType": "pickup",
        "paymentMethod": "cash",
        "note": "Test order without address",
        "subtotal": 250.0,
        "deliveryFee": 0.0,
        "platformFee": 0.0,
        "gst": 0.0,
        "promoDiscount": 0.0,
        "total": 250.0
        # Note: No addressId field - should work now
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    print(f"Order data: {json.dumps(order_data, indent=2)}")
    print(f"Headers: {headers}")

    order_response = requests.post('http://localhost:8000/api/mobile/orders',
                                   json=order_data, headers=headers)

    print(f"Order response status: {order_response.status_code}")
    print(f"Order response: {order_response.text}")

    if order_response.status_code == 200:
        print("Order created successfully without address!")
    else:
        print("Order creation failed!")

def test_admin_order_creation_without_location():
    print("\n=== Admin Order Creation Test (Without Location) ===\n")

    # Create admin order without location/branch
    order_data = {
        "customer_id": "test-customer-id",
        "items": [{
            "item_name": "Test Shawarma",
            "quantity": 1,
            "price": 250.0
        }],
        "delivery_fee": 0.0,
        "tip": 0.0
        # Note: No location, branch, or address_id - should work now
    }

    headers = {
        'Content-Type': 'application/json'
    }

    print(f"Admin order data: {json.dumps(order_data, indent=2)}")

    order_response = requests.post('http://localhost:8000/api/orders',
                                   json=order_data, headers=headers)

    print(f"Admin order response status: {order_response.status_code}")
    print(f"Admin order response: {order_response.text}")

    if order_response.status_code == 200:
        print("Admin order created successfully without location!")
    else:
        print("Admin order creation failed!")

if __name__ == "__main__":
    test_order_creation_without_address()
    test_admin_order_creation_without_location()