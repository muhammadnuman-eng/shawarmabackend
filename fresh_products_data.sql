-- Fresh Products Data with Live Image URLs
-- Delete existing products first
DELETE FROM products;

-- Insert fresh categories
INSERT OR REPLACE INTO categories (id, name, description, created_at) VALUES
('cat_001', 'Chicken Shawarma', 'Authentic chicken shawarma dishes', datetime('now')),
('cat_002', 'Beef Shawarma', 'Premium beef shawarma selections', datetime('now')),
('cat_003', 'Lamb Shawarma', 'Traditional lamb shawarma dishes', datetime('now')),
('cat_004', 'Vegetarian', 'Delicious vegetarian options', datetime('now')),
('cat_005', 'Sides', 'Fries, rice bowls and sides', datetime('now')),
('cat_006', 'Family Deals', 'Large portions and family meals', datetime('now'));

-- Insert fresh products with live image URLs
INSERT INTO products (id, name, price, image, description, category_id, rating, reviews_count, order_count, is_available, status, created_at, updated_at) VALUES
-- Chicken Shawarma
('prod_001', 'Classic Chicken Shawarma', 250.00,
 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=300&fit=crop',
 'Tender chicken marinated in traditional spices, wrapped in warm pita bread with garlic sauce and fresh vegetables',
 'cat_001', 4.5, 25, 120, 1, 'Available', datetime('now'), datetime('now')),

('prod_002', 'Chicken Shawarma Plate', 280.00,
 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400&h=300&fit=crop',
 'Chicken shawarma with rice, salad, and traditional sauces. Served with pickles and tahini',
 'cat_001', 4.3, 18, 85, 1, 'Available', datetime('now'), datetime('now')),

('prod_003', 'Spicy Chicken Shawarma', 270.00,
 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
 'Extra spicy chicken shawarma with special chili marinade and hot sauce',
 'cat_001', 4.4, 15, 67, 1, 'Available', datetime('now'), datetime('now')),

-- Beef Shawarma
('prod_004', 'Beef Shawarma Wrap', 300.00,
 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=300&fit=crop',
 'Slow-cooked beef with special blend of Middle Eastern spices, served with tahini sauce',
 'cat_002', 4.7, 32, 150, 1, 'Available', datetime('now'), datetime('now')),

('prod_005', 'Beef Shawarma Plate', 330.00,
 'https://images.unsplash.com/photo-1541599468348-e96984315621?w=400&h=300&fit=crop',
 'Beef shawarma with rice, salad, and traditional accompaniments',
 'cat_002', 4.6, 28, 95, 1, 'Available', datetime('now'), datetime('now')),

('prod_006', 'Premium Beef Shawarma', 350.00,
 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=300&fit=crop',
 'Premium cut beef shawarma with extra spices and special preparation',
 'cat_002', 4.8, 22, 78, 1, 'Available', datetime('now'), datetime('now')),

-- Lamb Shawarma
('prod_007', 'Lamb Shawarma Plate', 350.00,
 'https://images.unsplash.com/photo-1551782450-17144efb5723?w=400&h=300&fit=crop',
 'Juicy lamb shawarma served on a bed of rice with salad and yogurt sauce',
 'cat_003', 4.6, 20, 90, 1, 'Available', datetime('now'), datetime('now')),

('prod_008', 'Lamb Shawarma Wrap', 320.00,
 'https://images.unsplash.com/photo-1593001874117-c99c800e3eb7?w=400&h=300&fit=crop',
 'Tender lamb shawarma wrapped in pita with garlic sauce and vegetables',
 'cat_003', 4.5, 16, 65, 1, 'Available', datetime('now'), datetime('now')),

-- Vegetarian Options
('prod_009', 'Falafel Shawarma', 180.00,
 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop',
 'Crispy falafel balls with tahini sauce and fresh vegetables in pita bread',
 'cat_004', 4.1, 12, 45, 1, 'Available', datetime('now'), datetime('now')),

('prod_010', 'Vegetarian Shawarma', 200.00,
 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop',
 'Grilled vegetables and halloumi cheese with herbs, perfect for vegetarians',
 'cat_004', 4.2, 15, 60, 1, 'Available', datetime('now'), datetime('now')),

('prod_011', 'Halloumi Wrap', 220.00,
 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=300&fit=crop',
 'Grilled halloumi cheese with vegetables and special sauce',
 'cat_004', 4.0, 10, 35, 1, 'Available', datetime('now'), datetime('now')),

-- Sides
('prod_012', 'Shawarma Fries', 150.00,
 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400&h=300&fit=crop',
 'Crispy fries topped with shawarma meat and special garlic sauce',
 'cat_005', 4.4, 22, 100, 1, 'Available', datetime('now'), datetime('now')),

('prod_013', 'Shawarma Rice Bowl', 220.00,
 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
 'Shawarma meat over seasoned rice with vegetables and sauce',
 'cat_013', 4.3, 16, 70, 1, 'Available', datetime('now'), datetime('now')),

('prod_014', 'Garlic Sauce', 50.00,
 'https://images.unsplash.com/photo-1541599468348-e96984315621?w=400&h=300&fit=crop',
 'Authentic garlic sauce - perfect accompaniment for shawarma',
 'cat_005', 4.5, 8, 40, 1, 'Available', datetime('now'), datetime('now')),

-- Family Deals
('prod_015', 'Family Shawarma Deal', 750.00,
 'https://images.unsplash.com/photo-1551782450-17144efb5723?w=400&h=300&fit=crop',
 'Large family portion with multiple shawarmas, sides, and drinks',
 'cat_006', 4.6, 19, 40, 1, 'Available', datetime('now'), datetime('now')),

('prod_016', 'Mega Family Feast', 2500.00,
 'https://images.unsplash.com/photo-1593001874117-c99c800e3eb7?w=400&h=300&fit=crop',
 'Complete family meal with 5 shawarmas, large fries, drinks, and desserts',
 'cat_006', 4.9, 35, 25, 1, 'Available', datetime('now'), datetime('now')),

('prod_017', 'Ultimate Family Combo', 3200.00,
 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop',
 'Everything included: multiple meats, sides, drinks, and dessert platter',
 'cat_006', 5.0, 42, 15, 1, 'Available', datetime('now'), datetime('now')),

('prod_018', 'Party Size Deal', 2800.00,
 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop',
 'Perfect for parties - serves 8-10 people with variety of items',
 'cat_006', 4.7, 24, 30, 1, 'Available', datetime('now'), datetime('now'));

-- Update menu items with additional data for better functionality
UPDATE products SET
  main_components = '["Chicken", "Garlic Sauce", "Pita Bread", "Vegetables"]'
WHERE category_id = 'cat_001';

UPDATE products SET
  main_components = '["Beef", "Tahini Sauce", "Pita Bread", "Pickles"]'
WHERE category_id = 'cat_002';

UPDATE products SET
  main_components = '["Lamb", "Yogurt Sauce", "Pita Bread", "Onions"]'
WHERE category_id = 'cat_003';

UPDATE products SET
  main_components = '["Falafel", "Tahini", "Pita Bread", "Vegetables"]'
WHERE category_id = 'cat_004';

UPDATE products SET
  main_components = '["Fries", "Garlic Sauce", "Cheese"]'
WHERE id = 'prod_012';

UPDATE products SET
  main_components = '["Rice", "Meat", "Vegetables", "Sauce"]'
WHERE id = 'prod_013';

-- Add spicy elements for relevant products
UPDATE products SET
  spicy_elements = '["Extra Spicy", "Mild Spicy", "No Spice"]'
WHERE name LIKE '%Spicy%' OR name LIKE '%Hot%';

-- Add customization options
UPDATE products SET
  customization_options = '{"breadType": ["Pita", "Wrap"], "filling": ["Regular", "Extra"], "sauce": ["Garlic", "Tahini", "Hot"], "spiceLevel": ["Mild", "Medium", "Hot", "Extra Hot"]}'
WHERE category_id IN ('cat_001', 'cat_002', 'cat_003');

-- Show results
SELECT
    p.id,
    p.name,
    c.name as category,
    printf('Rs. %.0f', p.price) as price,
    p.rating,
    p.reviews_count,
    p.order_count,
    CASE WHEN p.is_available = 1 THEN 'Available' ELSE 'Unavailable' END as status
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
ORDER BY c.name, p.price DESC;

-- Count products by category
SELECT
    c.name as category,
    COUNT(p.id) as product_count
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name
ORDER BY c.name;
