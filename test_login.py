import requests

try:
    response = requests.post('http://localhost:8000/api/auth/login',
                           json={'email': 'test@example.com', 'password': 'password123'})
    print(f'Login test status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('Login successful!')
        print(f'User: {data["user"]["name"]}')
        print(f'Token length: {len(data["token"])}')
    else:
        print(f'Login failed: {response.text}')
except Exception as e:
    print(f'Login test failed: {e}')
