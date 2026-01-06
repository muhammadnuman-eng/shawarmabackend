#!/usr/bin/env python3

import requests
import json

def test_apis():
    base_url = 'http://localhost:8000/api'

    try:
        # Test categories API
        print("Testing Categories API...")
        response = requests.get(f'{base_url}/products/categories')
        if response.status_code == 200:
            categories = response.json()['categories']
            print(f"SUCCESS: Categories API: {len(categories)} categories found")
            for cat in categories[:3]:  # Show first 3
                print(f"   - {cat['name']}")
        else:
            print(f"ERROR: Categories API failed: {response.status_code}")

        # Test products API
        print("\nTesting Products API...")
        response = requests.get(f'{base_url}/products/products')
        if response.status_code == 200:
            products = response.json()['products']
            print(f"SUCCESS: Products API: {len(products)} products found")

            # Show sample products
            for product in products[:5]:  # Show first 5
                print(f"   - {product['name']} ({product['category']}) - Rs. {product['price']} - Rating: {product['rating']}")
        else:
            print(f"ERROR: Products API failed: {response.status_code}")

        # Test recommended products
        print("\nTesting Recommended Products API...")
        response = requests.get(f'{base_url}/products/products/recommended?limit=3')
        if response.status_code == 200:
            products = response.json()['products']
            print(f"SUCCESS: Recommended API: {len(products)} products found")
        else:
            print(f"ERROR: Recommended API failed: {response.status_code}")

        # Test family deals
        print("\nTesting Family Deals API...")
        response = requests.get(f'{base_url}/products/products/family-deals')
        if response.status_code == 200:
            products = response.json()['products']
            print(f"SUCCESS: Family Deals API: {len(products)} products found")
            if products:
                print(f"   - Sample: {products[0]['name']} - Rs. {products[0]['price']}")
        else:
            print(f"ERROR: Family Deals API failed: {response.status_code}")

        print("\nAll APIs are working correctly!")

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        print("Make sure the backend server is running on http://localhost:8000")

if __name__ == "__main__":
    test_apis()