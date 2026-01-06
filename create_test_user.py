#!/usr/bin/env python3
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from datetime import datetime
import uuid

def create_test_user():
    db = SessionLocal()

    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == 'test@example.com').first()

        if existing_user:
            print(f"Test user already exists: {existing_user.email}")
            print("Updating password to 'password123'...")
            existing_user.password_hash = get_password_hash('password123')
            existing_user.updated_at = datetime.utcnow()
            db.commit()
            print("Password updated successfully!")
        else:
            # Create new test user
            test_user = User(
                id=str(uuid.uuid4()),
                name='Test User',
                email='test@example.com',
                password_hash=get_password_hash('password123'),
                is_admin=False,
                is_online=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(test_user)
            db.commit()
            print(f"Test user created: {test_user.email}")

        # Verify the user
        user = db.query(User).filter(User.email == 'test@example.com').first()
        if user:
            print(f"User verification: {user.email}")
            print(f"Password hash: {user.password_hash[:30]}...")
            # Test password verification
            from app.core.security import verify_password
            is_valid = verify_password('password123', user.password_hash)
            print(f"Password verification: {'PASS' if is_valid else 'FAIL'}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
