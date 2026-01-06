#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('shawarma_local.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
conn.close()

print('Tables in database:')
for table in tables:
    print(f'  - {table[0]}')
