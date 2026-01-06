#!/usr/bin/env python3
"""
Check if products are available in the database
"""

import sqlite3
import os

def check_products():
    db_path = 'shawarma_local.db'

    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if menu_items table exists (this seems to be the actual table name)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu_items'")
        menu_table_exists = cursor.fetchone()

        # Also check products table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        products_table_exists = cursor.fetchone()

        print('Database Tables:')
        if menu_table_exists:
            print('[OK] menu_items table exists')
        else:
            print('[NO] menu_items table does not exist')

        if products_table_exists:
            print('[OK] products table exists')
        else:
            print('[NO] products table does not exist')

        # Check menu_items table (primary table)
        if menu_table_exists:
            cursor.execute('SELECT COUNT(*) FROM menu_items')
            total_menu_items = cursor.fetchone()[0]
            print(f'\nMenu Items: {total_menu_items}')

            if total_menu_items > 0:
                # Check categories
                cursor.execute('SELECT DISTINCT category FROM menu_items WHERE category IS NOT NULL')
                categories = cursor.fetchall()
                print('Categories found:', [cat[0] for cat in categories])

                # Check for specific categories
                categories_to_check = ['high_demand', 'recommended', 'family_deals', 'fastest']
                for cat in categories_to_check:
                    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE category = ?', (cat,))
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f'[YES] {cat}: {count} items')
                    else:
                        print(f'[NO] {cat}: 0 items')

                # Check order counts (for high demand)
                cursor.execute('SELECT COUNT(*) FROM menu_items WHERE order_count > 0')
                items_with_orders = cursor.fetchone()[0]
                print(f'Items with orders: {items_with_orders}')

                # Show sample menu items
                cursor.execute('SELECT id, name, category, price, order_count FROM menu_items LIMIT 5')
                sample_items = cursor.fetchall()
                print('\nSample menu items:')
                for item in sample_items:
                    print(f'  - ID: {item[0]}, Name: {item[1]}, Category: {item[2]}, Price: {item[3]}, Orders: {item[4]}')

        # Check products table if it exists
        if products_table_exists:
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]
            print(f'\nProducts table items: {total_products}')

            if total_products > 0:
                cursor.execute('SELECT id, name, category, price FROM products LIMIT 3')
                sample_products = cursor.fetchall()
                print('Sample products from products table:')
                for product in sample_products:
                    print(f'  - ID: {product[0]}, Name: {product[1]}, Category: {product[2]}, Price: {product[3]}')

        conn.close()

    except Exception as e:
        print(f'[ERROR] Error checking database: {e}')

if __name__ == "__main__":
    check_products()
