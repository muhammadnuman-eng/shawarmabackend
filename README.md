# Shawarma Stop Admin Backend API

Production-ready FastAPI backend with MySQL for Shawarma Stop Admin Panel.

## Features

- **Orders Management** - Create, read, update, delete orders with status tracking
- **Customer Management** - Customer CRUD operations with membership tracking
- **Staff Management** - Staff management with role and branch assignment
- **Menu Management** - Menu items, categories, and mobile app sections
- **Transactions** - Payment transaction tracking
- **Reviews & Ratings** - Customer reviews and ratings system
- **Dashboard** - Real-time statistics and analytics
- **Roles & Permissions** - Role-based access control

## Tech Stack

- **FastAPI** - Modern Python web framework
- **MySQL** - Production database
- **SQLAlchemy** - ORM for database operations
- **PyMySQL** - MySQL database connector
- **Pydantic** - Data validation
- **Alembic** - Database migrations

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── orders.py
│   │       ├── customers.py
│   │       ├── staff.py
│   │       ├── menu.py
│   │       ├── transactions.py
│   │       ├── reviews.py
│   │       ├── roles.py
│   │       └── dashboard.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── order.py
│   │   ├── customer.py
│   │   ├── staff.py
│   │   ├── menu.py
│   │   ├── review.py
│   │   ├── transaction.py
│   │   └── role.py
│   ├── schemas/
│   │   ├── order.py
│   │   ├── customer.py
│   │   ├── staff.py
│   │   ├── menu.py
│   │   ├── review.py
│   │   ├── transaction.py
│   │   └── dashboard.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

Create a MySQL database:

```sql
CREATE DATABASE shwarma CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Environment Configuration

Create a `.env` file in the backend directory:

```env
# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=shwarma

# Application Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Run Database Migrations

The database tables will be created automatically on first run. For production, use Alembic:

```bash
alembic upgrade head
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics

### Orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders` - Get all orders (with filters)
- `GET /api/v1/orders/{order_id}` - Get order by ID
- `PATCH /api/v1/orders/{order_id}` - Update order
- `DELETE /api/v1/orders/{order_id}` - Delete order

### Customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers` - Get all customers
- `GET /api/v1/customers/{customer_id}` - Get customer by ID
- `PATCH /api/v1/customers/{customer_id}` - Update customer
- `DELETE /api/v1/customers/{customer_id}` - Delete customer

### Staff
- `POST /api/v1/staff` - Create staff member
- `GET /api/v1/staff` - Get all staff (with filters)
- `GET /api/v1/staff/{staff_id}` - Get staff by ID
- `PATCH /api/v1/staff/{staff_id}` - Update staff
- `DELETE /api/v1/staff/{staff_id}` - Delete staff

### Menu
- `POST /api/v1/menu/categories` - Create category
- `GET /api/v1/menu/categories` - Get all categories
- `DELETE /api/v1/menu/categories/{category_id}` - Delete category
- `POST /api/v1/menu/items` - Create menu item
- `GET /api/v1/menu/items` - Get all menu items
- `GET /api/v1/menu/items/{item_id}` - Get menu item by ID
- `PATCH /api/v1/menu/items/{item_id}` - Update menu item
- `DELETE /api/v1/menu/items/{item_id}` - Delete menu item
- `POST /api/v1/menu/sections` - Create menu section
- `GET /api/v1/menu/sections` - Get all menu sections
- `GET /api/v1/menu/sections/{section_id}` - Get menu section by ID
- `DELETE /api/v1/menu/sections/{section_id}` - Delete menu section

### Transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - Get all transactions (with filters)
- `GET /api/v1/transactions/{transaction_id}` - Get transaction by ID

### Reviews
- `POST /api/v1/reviews` - Create review
- `GET /api/v1/reviews` - Get all reviews (with filters)
- `GET /api/v1/reviews/{review_id}` - Get review by ID

### Roles
- `GET /api/v1/roles/permissions` - Get all permissions
- `GET /api/v1/roles/roles` - Get all roles

## Production Deployment

1. Set proper environment variables
2. Use a production ASGI server like Gunicorn with Uvicorn workers
3. Set up proper database connection pooling
4. Enable HTTPS
5. Set up proper logging and monitoring
6. Use environment-specific configurations

## License

Proprietary - Shawarma Stop Admin Panel

