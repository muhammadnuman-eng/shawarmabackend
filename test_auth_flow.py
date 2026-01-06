import requests
import json

print("=== Authentication Flow Test ===\n")

# Test 1: Login
print("1. Testing Login...")
response = requests.post('http://localhost:8000/api/auth/login',
                        json={'email': 'test@example.com', 'password': 'password123'})

if response.status_code == 200:
    data = response.json()
    token = data['token']
    user = data['user']
    print(f"SUCCESS: Login successful!")
    print(f"   User: {user['email']}")
    print(f"   Token: {token[:30]}...")

    # Test 2: Authenticated Favorites
    print("\n2. Testing Authenticated Favorites...")
    headers = {'Authorization': f'Bearer {token}'}
    fav_response = requests.get('http://localhost:8000/api/favorites', headers=headers)
    print(f"   Status: {fav_response.status_code}")
    if fav_response.status_code == 200:
        print("   SUCCESS: Favorites accessible!")
    else:
        print(f"   ERROR: Favorites failed: {fav_response.text}")

    # Test 3: Authenticated Cart
    print("\n3. Testing Authenticated Cart Add...")
    cart_data = {'productId': '39cd0e51-8345-4908-900c-3a9bdcad549d', 'quantity': 1}
    cart_response = requests.post('http://localhost:8000/api/cart',
                                 json=cart_data, headers=headers)
    print(f"   Status: {cart_response.status_code}")
    if cart_response.status_code == 200:
        print("   SUCCESS: Cart add successful!")
    else:
        print(f"   ERROR: Cart add failed: {cart_response.text}")

    # Test 4: Unauthenticated Request (should fail)
    print("\n4. Testing Unauthenticated Request...")
    no_auth_response = requests.get('http://localhost:8000/api/favorites')
    print(f"   Status: {no_auth_response.status_code}")
    if no_auth_response.status_code == 401:
        print("   SUCCESS: Properly rejects unauthenticated requests!")
    else:
        print(f"   WARNING: Unexpected response: {no_auth_response.status_code}")

else:
    print(f"Login failed: {response.status_code} - {response.text}")

print("\n=== Test Complete ===")
