#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('shawarma_local.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

# Check if otps table exists
cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="otps"')
otp_table = cursor.fetchone()
if otp_table:
    print("OTPs table exists")
    cursor.execute('SELECT COUNT(*) FROM otps')
    count = cursor.fetchone()[0]
    print(f"OTP records count: {count}")

    # Show recent OTPs
    cursor.execute('SELECT email, otp_code, purpose, created_at FROM otps ORDER BY created_at DESC LIMIT 5')
    recent_otps = cursor.fetchall()
    print("Recent OTPs:")
    for otp in recent_otps:
        print(f"  Email: {otp[0]}, Code: {otp[1]}, Purpose: {otp[2]}, Created: {otp[3]}")
else:
    print("OTPs table does not exist")

conn.close()













