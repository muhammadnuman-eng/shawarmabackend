#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite/MySQL to PostgreSQL
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base
from app.models import *
import uuid
from datetime import datetime

# Source database (current SQLite/MySQL)
SOURCE_DB_URL = "sqlite:///./shawarma_local.db"  # Change this if using MySQL

# Target database (PostgreSQL)
TARGET_DB_URL = "postgresql://postgres:test123@localhost:5432/shawarmabackend"

def get_source_engine():
    """Get source database engine"""
    return create_engine(SOURCE_DB_URL, echo=False)

def get_target_engine():
    """Get target PostgreSQL engine"""
    return create_engine(
        TARGET_DB_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        pool_size=10,
        max_overflow=20
    )

def create_postgres_tables(target_engine):
    """Create all tables in PostgreSQL"""
    print("Creating tables in PostgreSQL...")
    try:
        Base.metadata.create_all(bind=target_engine)
        print("SUCCESS: All tables created in PostgreSQL")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create tables: {e}")
        return False

def migrate_table_data(source_engine, target_engine, table_name, model_class):
    """Migrate data for a specific table"""
    print(f"Migrating table: {table_name}")

    try:
        source_session = sessionmaker(bind=source_engine)()
        target_session = sessionmaker(bind=target_engine)()

        # Get all records from source
        records = source_session.query(model_class).all()
        total_records = len(records)

        if total_records == 0:
            print(f"  No records to migrate for {table_name}")
            return True

        print(f"  Migrating {total_records} records...")

        # Insert records into target
        for i, record in enumerate(records, 1):
            # Create a dict of the record's data
            record_dict = {}
            for column in model_class.__table__.columns:
                value = getattr(record, column.name)
                # Handle UUID conversion for PostgreSQL
                if column.name == 'id' and isinstance(value, str):
                    try:
                        # Ensure it's a valid UUID
                        uuid.UUID(value)
                        record_dict[column.name] = value
                    except ValueError:
                        # Generate new UUID if invalid
                        record_dict[column.name] = str(uuid.uuid4())
                else:
                    record_dict[column.name] = value

            # Create new instance and add to target session
            new_record = model_class(**record_dict)
            target_session.add(new_record)

            # Commit in batches to avoid memory issues
            if i % 100 == 0:
                target_session.commit()
                print(f"    Processed {i}/{total_records} records...")

        # Final commit
        target_session.commit()
        print(f"SUCCESS: Migrated {total_records} records for {table_name}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to migrate {table_name}: {e}")
        target_session.rollback()
        return False
    finally:
        source_session.close()
        target_session.close()

def get_all_models():
    """Get all model classes for migration"""
    from app.models.user import (
        User, OTP, Address, CartItem, Favorite, Notification,
        NotificationSettings, LoyaltyPoint, Reward, SearchHistory,
        PaymentCard, Chat, ChatParticipant, ChatMessage, PromoCode
    )
    from app.models.menu import Category, MenuItem, MenuSection, MenuSectionItem
    from app.models.order import Order, OrderItem
    from app.models.staff import Staff
    from app.models.customer import Customer
    from app.models.review import Review
    from app.models.transaction import Transaction
    from app.models.role import Role, Permission

    return [
        (User, "users"),
        (OTP, "otps"),
        (Address, "addresses"),
        (CartItem, "cart_items"),
        (Favorite, "favorites"),
        (Notification, "notifications"),
        (NotificationSettings, "notification_settings"),
        (LoyaltyPoint, "loyalty_points"),
        (Reward, "rewards"),
        (SearchHistory, "search_history"),
        (PaymentCard, "payment_cards"),
        (Chat, "chats"),
        (ChatParticipant, "chat_participants"),
        (ChatMessage, "chat_messages"),
        (PromoCode, "promo_codes"),
        (Category, "categories"),
        (MenuItem, "products"),  # Note: products table
        (MenuSection, "menu_sections"),
        (MenuSectionItem, "menu_section_items"),
        (Order, "orders"),
        (OrderItem, "order_items"),
        (Staff, "staff"),
        (Customer, "customers"),
        (Review, "reviews"),
        (Transaction, "transactions"),
        (Role, "roles"),
        (Permission, "permissions"),
    ]

def main():
    """Main migration function"""
    print("Starting migration from SQLite to PostgreSQL...")
    print(f"Source: {SOURCE_DB_URL}")
    print(f"Target: {TARGET_DB_URL}")
    print("-" * 50)

    # Test connections
    try:
        source_engine = get_source_engine()
        with source_engine.connect() as conn:
            print("SUCCESS: Connected to source database")
    except Exception as e:
        print(f"ERROR: Cannot connect to source database: {e}")
        return False

    try:
        target_engine = get_target_engine()
        with target_engine.connect() as conn:
            print("SUCCESS: Connected to target PostgreSQL database")
    except Exception as e:
        print(f"ERROR: Cannot connect to target database: {e}")
        return False

    # Create tables in PostgreSQL
    if not create_postgres_tables(target_engine):
        return False

    # Migrate data for each table
    models_to_migrate = get_all_models()
    success_count = 0

    for model_class, table_name in models_to_migrate:
        if migrate_table_data(source_engine, target_engine, table_name, model_class):
            success_count += 1
        else:
            print(f"WARNING: Failed to migrate {table_name}")

    print("-" * 50)
    print(f"Migration completed: {success_count}/{len(models_to_migrate)} tables migrated successfully")

    if success_count == len(models_to_migrate):
        print("SUCCESS: All data migrated to PostgreSQL!")
        print("You can now update your DATABASE_URL to use PostgreSQL.")
        return True
    else:
        print("WARNING: Some tables failed to migrate. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
