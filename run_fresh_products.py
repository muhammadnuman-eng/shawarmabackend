#!/usr/bin/env python3

import sqlite3
from app.core.database import engine
import os

def run_fresh_products():
    # Get database path from engine
    db_path = str(engine.url).replace('sqlite:///', '')

    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return

    print(f"Using database: {db_path}")

    # Read SQL file
    sql_file = 'fresh_products_data.sql'
    if not os.path.exists(sql_file):
        print(f"SQL file not found: {sql_file}")
        return

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # Execute SQL script
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql_script)
        conn.commit()
        print("SUCCESS: SQL script executed successfully!")

        # Verify products were added
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        product_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM categories')
        category_count = cursor.fetchone()[0]

        print("Database Summary:")
        print(f"   Categories: {category_count}")
        print(f"   Products: {product_count}")

        # Show products by category
        cursor.execute('''
            SELECT c.name as category, COUNT(p.id) as count
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY c.id, c.name
            ORDER BY c.name
        ''')

        print("\nProducts by Category:")
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]} products")

        # Show sample products
        cursor.execute('''
            SELECT p.name, c.name as category, printf('Rs. %.0f', p.price) as price, p.rating
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
            LIMIT 5
        ''')

        print("\nSample Products:")
        for row in cursor.fetchall():
            print(f"   {row[0]} ({row[1]}) - {row[2]} - Rating: {row[3]}")

    except Exception as e:
        print(f"ERROR: Error executing SQL script: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_fresh_products()
