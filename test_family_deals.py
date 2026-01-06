import requests

try:
    response = requests.get('http://localhost:8000/api/products/family-deals?limit=5')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        print(f'Products returned: {len(products)}')
        for p in products[:3]:
            print(f'  - {p["name"]}: Rs {p["price"]}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Connection error: {e}')
    print('Make sure backend server is running on localhost:8000')
