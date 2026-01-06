-- Sample Products Data - Only Required Fields
-- This script shows how to insert products with only the 4 required fields

-- Basic products with only required fields
INSERT INTO products (id, name, price, image, description) VALUES
('prod_001', 'Classic Chicken Shawarma', 250.00,
 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
 'Tender chicken marinated in traditional spices, wrapped in warm pita bread with garlic sauce'),

('prod_002', 'Beef Shawarma Wrap', 300.00,
 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400',
 'Slow-cooked beef with special blend of Middle Eastern spices, served with tahini'),

('prod_003', 'Lamb Shawarma Plate', 350.00,
 'https://images.unsplash.com/photo-1541599468348-e96984315621?w=400',
 'Juicy lamb shawarma served on a bed of rice with salad and yogurt sauce'),

('prod_004', 'Vegetarian Shawarma', 200.00,
 'https://images.unsplash.com/photo-1551782450-17144efb5723?w=400',
 'Grilled vegetables and halloumi cheese with herbs, perfect for vegetarians'),

('prod_005', 'Falafel Shawarma', 180.00,
 'https://images.unsplash.com/photo-1593001874117-c99c800e3eb7?w=400',
 'Crispy falafel balls with tahini sauce and fresh vegetables in pita bread'),

('prod_006', 'Chicken Shawarma Plate', 280.00,
 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400',
 'Chicken shawarma with rice, salad, and traditional sauces'),

('prod_007', 'Mixed Grill Shawarma', 400.00,
 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400',
 'Combination of chicken, beef, and lamb with all traditional accompaniments'),

('prod_008', 'Shawarma Fries', 150.00,
 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400',
 'Crispy fries topped with shawarma meat and special garlic sauce'),

('prod_009', 'Shawarma Rice Bowl', 220.00,
 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400',
 'Shawarma meat over seasoned rice with vegetables and sauce'),

('prod_010', 'Family Shawarma Deal', 750.00,
 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400',
 'Large family portion with multiple shawarmas, sides, and drinks'),

('prod_011', 'Mega Family Feast', 2500.00,
 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
 'Complete family meal with 5 shawarmas, large fries, drinks, and desserts'),

('prod_012', 'Ultimate Family Combo', 3200.00,
 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400',
 'Everything included: multiple meats, sides, drinks, and dessert platter'),

('prod_013', 'Party Size Deal', 2800.00,
 'https://images.unsplash.com/photo-1541599468348-e96984315621?w=400',
 'Perfect for parties - serves 8-10 people with variety of items');

-- Show the inserted data
SELECT
    id,
    name,
    CONCAT('Rs. ', FORMAT(price, 0)) as price,
    LEFT(description, 50) as short_description,
    image
FROM products
ORDER BY created_at DESC
LIMIT 10;
