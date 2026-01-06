-- SQL Script to Add Addresses to Database
-- Run this script in your SQLite database

-- First, create system user for pickup addresses (if not exists)
INSERT OR IGNORE INTO users (id, name, email, is_admin, created_at, updated_at)
VALUES ('system-user-pickup', 'System', 'system@shawarma.local', 1, datetime('now'), datetime('now'));

-- Create sample user for delivery addresses (if not exists)
INSERT OR IGNORE INTO users (id, name, email, phone_number, is_admin, created_at, updated_at)
VALUES ('sample-user-delivery', 'Test User', 'testuser@example.com', '+923001234567', 0, datetime('now'), datetime('now'));

-- Add pickup addresses (system user)
INSERT OR REPLACE INTO addresses (id, name, address, latitude, longitude, type, user_id, is_default, created_at, updated_at)
VALUES
('dha-phase-4', 'DHA Phase 4', 'Building # 157, DHA Phase 4 Sector CCA Dha Phase 4, Lahore, 52000', 31.4697, 74.2728, 'pickup', 'system-user-pickup', 0, datetime('now'), datetime('now')),

('main-pia-road', 'Main PIA Road', '39D, Main PIA Commercial Road, Block D Pia Housing Scheme, Lahore, 54770', 31.5204, 74.3528, 'pickup', 'system-user-pickup', 0, datetime('now'), datetime('now')),

('lake-city', 'Lake City', '1160 Street 44, Block M 3 A Lake City, Lahore', 31.4833, 74.3833, 'pickup', 'system-user-pickup', 0, datetime('now'), datetime('now'));

-- Add sample delivery addresses (sample user)
INSERT OR REPLACE INTO addresses (id, name, address, latitude, longitude, type, user_id, is_default, created_at, updated_at)
VALUES
('user-home-' || lower(hex(randomblob(4))), 'Home', '123 Main Street, Johar Town, Lahore, 54000', 31.5204, 74.3587, 'home', 'sample-user-delivery', 1, datetime('now'), datetime('now')),

('user-office-' || lower(hex(randomblob(4))), 'Office', '456 Business Avenue, Gulberg, Lahore, 54600', 31.5204, 74.3587, 'work', 'sample-user-delivery', 0, datetime('now'), datetime('now'));

-- Verify the data was inserted
SELECT 'Addresses added successfully!' as status;

-- Show summary
SELECT
    'Total Addresses' as type,
    COUNT(*) as count
FROM addresses
UNION ALL
SELECT
    'Pickup Addresses' as type,
    COUNT(*) as count
FROM addresses
WHERE type = 'pickup'
UNION ALL
SELECT
    'Delivery Addresses' as type,
    COUNT(*) as count
FROM addresses
WHERE type != 'pickup';

-- Show all addresses
SELECT
    a.name,
    a.address,
    a.type,
    u.email as user_email,
    a.is_default
FROM addresses a
JOIN users u ON a.user_id = u.id
ORDER BY a.type, a.name;
