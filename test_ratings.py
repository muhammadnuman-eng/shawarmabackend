#!/usr/bin/env python3

import requests

def test_ratings():
    response = requests.get('http://localhost:8000/api/products')
    if response.status_code == 200:
        data = response.json()
        print("API Response Ratings:")
        for product in data['products'][:5]:  # First 5 products
            print(f"  {product['name']}: rating={product['rating']}, reviews={product['reviewsCount']}")

if __name__ == "__main__":
    test_ratings()
