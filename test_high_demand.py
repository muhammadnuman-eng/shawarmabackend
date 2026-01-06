import requests

try:
    response = requests.get('http://localhost:8000/api/products/high-demand?limit=3')
    print(f'High-demand API status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        print(f'Success! Found {len(products)} products')
        for p in products[:2]:
            print(f'  - {p["name"]}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'API test failed: {e}')
