-- =============================================
-- SHAWARMA BACKEND - SAMPLE DATA INSERTION
-- Run this script in pgAdmin to populate your database
-- =============================================

-- =============================================
-- 1. INSERT CATEGORIES
-- =============================================

INSERT INTO categories (id, name, description, icon, image, created_at) VALUES
('cat_fatayers_001', 'Fatayers', 'Traditional Lebanese fatayer pastries filled with various toppings', 'pie', 'https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=400&h=300&fit=crop', NOW()),
('cat_shawarma_001', 'Shawarma', 'Authentic Middle Eastern shawarma wraps and plates', 'wrap', 'https://images.unsplash.com/photo-1529006557810-27490341240f?w=400&h=300&fit=crop', NOW()),
('cat_appetizers_001', 'Appetizers', 'Delicious starters and side dishes', 'snack', 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop', NOW()),
('cat_desserts_001', 'Desserts', 'Sweet treats and traditional desserts', 'cake', 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop', NOW()),
('cat_drinks_001', 'Drinks', 'Refreshing beverages and traditional drinks', 'drink', 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop', NOW()),
('cat_family_deals_001', 'Family Deals', 'Special meal deals for families', 'family', 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop', NOW());

-- =============================================
-- 2. INSERT PRODUCTS
-- =============================================

-- FATAYERS
INSERT INTO products (id, name, category_id, price, description, image, images, status, is_available, main_components, spicy_elements, additional_flavor, optional_add_ons, customization_options, rating, reviews_count, order_count, distance, delivery_time, created_at, updated_at) VALUES
('prod_fatayer_cheese_001', 'Cheese Fatayer', 'cat_fatayers_001', 8.99,
 'Traditional Lebanese cheese pastry with mozzarella and feta cheese',
 'https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Mozzarella Cheese", "price": 2.50}, {"name": "Feta Cheese", "price": 1.50}, {"name": "Fresh Dough", "price": 3.00}]',
 '["Mild"]',
 '[{"name": "Extra Cheese", "price": 2.00}, {"name": "Spinach", "price": 1.50}]',
 '[{"name": "Za''atar", "price": 0.50}, {"name": "Black Olives", "price": 1.00}]',
 '{"breadType": ["Thin Crust", "Thick Crust"], "spiceLevel": ["Mild", "Medium"]}',
 4.5, 23, 145, '2.1 km', '25-30 min', NOW(), NOW()),

('prod_fatayer_spinach_001', 'Spinach & Cheese Fatayer', 'cat_fatayers_001', 9.99,
 'Fresh spinach and cheese filling in crispy pastry',
 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Fresh Spinach", "price": 1.50}, {"name": "Mozzarella Cheese", "price": 2.50}, {"name": "Onion", "price": 0.80}, {"name": "Fresh Dough", "price": 3.00}]',
 '["Mild", "Medium"]',
 '[{"name": "Extra Cheese", "price": 2.00}, {"name": "Pine Nuts", "price": 2.50}]',
 '[{"name": "Sumac", "price": 0.50}, {"name": "Lemon", "price": 0.30}]',
 '{"breadType": ["Thin Crust", "Thick Crust"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.7, 31, 198, '2.1 km', '25-30 min', NOW(), NOW()),

('prod_fatayer_meat_001', 'Meat Fatayer', 'cat_fatayers_001', 11.99,
 'Ground beef and lamb with pine nuts in flaky pastry',
 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Ground Beef", "price": 4.00}, {"name": "Ground Lamb", "price": 3.50}, {"name": "Pine Nuts", "price": 2.50}, {"name": "Onion", "price": 0.80}, {"name": "Fresh Dough", "price": 3.00}]',
 '["Medium", "Hot"]',
 '[{"name": "Extra Meat", "price": 3.00}, {"name": "Cheese", "price": 2.00}]',
 '[{"name": "Cinnamon", "price": 0.50}, {"name": "Allspice", "price": 0.40}]',
 '{"breadType": ["Thin Crust", "Thick Crust"], "spiceLevel": ["Medium", "Hot", "Extra Hot"]}',
 4.8, 45, 267, '2.1 km', '25-30 min', NOW(), NOW());

-- SHAWARMA PRODUCTS
INSERT INTO products (id, name, category_id, price, description, image, images, status, is_available, main_components, spicy_elements, additional_flavor, optional_add_ons, customization_options, rating, reviews_count, order_count, distance, delivery_time, created_at, updated_at) VALUES
('prod_shawarma_chicken_001', 'Chicken Shawarma Wrap', 'cat_shawarma_001', 12.99,
 'Marinated chicken shawarma in pita bread with garlic sauce',
 'https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Marinated Chicken", "price": 6.00}, {"name": "Pita Bread", "price": 1.50}, {"name": "Garlic Sauce", "price": 1.00}, {"name": "Pickles", "price": 0.50}, {"name": "Tomato", "price": 0.80}, {"name": "Onion", "price": 0.60}]',
 '["Medium"]',
 '[{"name": "Extra Chicken", "price": 4.00}, {"name": "Cheese", "price": 1.50}]',
 '[{"name": "Hot Sauce", "price": 0.50}, {"name": "Tahini", "price": 1.00}, {"name": "French Fries", "price": 2.50}]',
 '{"breadType": ["Pita", "Wrap"], "filling": ["Chicken", "Chicken + Cheese"], "sides": ["Fries", "Rice", "Salad"], "sauces": ["Garlic", "Tahini", "Hot Sauce"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.6, 89, 423, '2.1 km', '20-25 min', NOW(), NOW()),

('prod_shawarma_beef_001', 'Beef Shawarma Wrap', 'cat_shawarma_001', 14.99,
 'Slow-cooked beef shawarma with traditional spices',
 'https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Marinated Beef", "price": 8.00}, {"name": "Pita Bread", "price": 1.50}, {"name": "Garlic Sauce", "price": 1.00}, {"name": "Pickles", "price": 0.50}, {"name": "Tomato", "price": 0.80}, {"name": "Parsley", "price": 0.40}]',
 '["Medium", "Hot"]',
 '[{"name": "Extra Beef", "price": 5.00}, {"name": "Cheese", "price": 1.50}]',
 '[{"name": "Hot Sauce", "price": 0.50}, {"name": "Tahini", "price": 1.00}, {"name": "French Fries", "price": 2.50}]',
 '{"breadType": ["Pita", "Wrap"], "filling": ["Beef", "Beef + Cheese"], "sides": ["Fries", "Rice", "Salad"], "sauces": ["Garlic", "Tahini", "Hot Sauce"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.7, 67, 345, '2.1 km', '20-25 min', NOW(), NOW()),

('prod_shawarma_mixed_001', 'Mixed Shawarma Plate', 'cat_shawarma_001', 16.99,
 'Chicken and beef shawarma served on a plate with rice and salad',
 'https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Marinated Chicken", "price": 4.00}, {"name": "Marinated Beef", "price": 5.00}, {"name": "Rice", "price": 2.00}, {"name": "Salad", "price": 1.50}, {"name": "Garlic Sauce", "price": 1.00}, {"name": "Pickles", "price": 0.50}]',
 '["Medium"]',
 '[{"name": "Extra Protein", "price": 4.50}, {"name": "Cheese", "price": 1.50}]',
 '[{"name": "Hot Sauce", "price": 0.50}, {"name": "Tahini", "price": 1.00}, {"name": "Bread", "price": 1.50}]',
 '{"protein": ["Chicken", "Beef", "Mixed"], "sides": ["Rice", "Fries", "Bread"], "sauces": ["Garlic", "Tahini", "Hot Sauce"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.8, 123, 567, '2.1 km', '25-30 min', NOW(), NOW()),

('prod_shawarma_lamb_001', 'Lamb Shawarma Wrap', 'cat_shawarma_001', 15.99,
 'Premium lamb shawarma with authentic spices',
 'https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Marinated Lamb", "price": 9.00}, {"name": "Pita Bread", "price": 1.50}, {"name": "Garlic Sauce", "price": 1.00}, {"name": "Pickles", "price": 0.50}, {"name": "Tomato", "price": 0.80}, {"name": "Onion", "price": 0.60}]',
 '["Medium", "Hot"]',
 '[{"name": "Extra Lamb", "price": 6.00}, {"name": "Cheese", "price": 1.50}]',
 '[{"name": "Hot Sauce", "price": 0.50}, {"name": "Tahini", "price": 1.00}, {"name": "French Fries", "price": 2.50}]',
 '{"breadType": ["Pita", "Wrap"], "filling": ["Lamb", "Lamb + Cheese"], "sides": ["Fries", "Rice", "Salad"], "sauces": ["Garlic", "Tahini", "Hot Sauce"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.9, 56, 298, '2.1 km', '20-25 min', NOW(), NOW());

-- APPETIZERS
INSERT INTO products (id, name, category_id, price, description, image, images, status, is_available, main_components, spicy_elements, additional_flavor, optional_add_ons, customization_options, rating, reviews_count, order_count, distance, delivery_time, created_at, updated_at) VALUES
('prod_hummus_001', 'Classic Hummus', 'cat_appetizers_001', 6.99,
 'Creamy chickpea dip served with pita bread and olive oil',
 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Chickpeas", "price": 2.50}, {"name": "Tahini", "price": 1.50}, {"name": "Lemon", "price": 0.50}, {"name": "Garlic", "price": 0.30}, {"name": "Pita Bread", "price": 1.00}, {"name": "Olive Oil", "price": 0.80}]',
 '["Mild"]',
 '[{"name": "Extra Pita", "price": 1.50}]',
 '[{"name": "Pine Nuts", "price": 2.00}, {"name": "Paprika", "price": 0.50}]',
 '{"size": ["Small", "Medium", "Large"], "extras": ["Pine Nuts", "Paprika", "Extra Pita"]}',
 4.4, 78, 234, '2.1 km', '15-20 min', NOW(), NOW()),

('prod_falafel_001', 'Falafel Plate', 'cat_appetizers_001', 8.99,
 'Crispy falafel balls with tahini sauce and salad',
 'https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Falafel Balls", "price": 4.00}, {"name": "Tahini Sauce", "price": 1.00}, {"name": "Lettuce", "price": 0.50}, {"name": "Tomato", "price": 0.80}, {"name": "Pickles", "price": 0.50}, {"name": "Pita Bread", "price": 1.00}]',
 '["Mild", "Medium"]',
 '[{"name": "Extra Falafel", "price": 2.50}]',
 '[{"name": "Hot Sauce", "price": 0.50}, {"name": "Hummus", "price": 1.50}]',
 '{"size": ["Small", "Medium", "Large"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.5, 92, 312, '2.1 km', '15-20 min', NOW(), NOW()),

('prod_fries_001', 'Seasoned Fries', 'cat_appetizers_001', 4.99,
 'Crispy fries seasoned with Middle Eastern spices',
 'https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Potatoes", "price": 2.00}, {"name": "Vegetable Oil", "price": 0.80}, {"name": "Salt", "price": 0.10}, {"name": "Za''atar", "price": 0.50}, {"name": "Paprika", "price": 0.40}]',
 '["Mild", "Medium"]',
 '[{"name": "Cheese", "price": 1.50}]',
 '[{"name": "Garlic Powder", "price": 0.30}, {"name": "Hot Sauce", "price": 0.50}]',
 '{"size": ["Small", "Medium", "Large"], "seasoning": ["Za''atar", "Paprika", "Garlic"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.2, 156, 423, '2.1 km', '10-15 min', NOW(), NOW());

-- DESSERTS
INSERT INTO products (id, name, category_id, price, description, image, images, status, is_available, main_components, spicy_elements, additional_flavor, optional_add_ons, customization_options, rating, reviews_count, order_count, distance, delivery_time, created_at, updated_at) VALUES
('prod_baklava_001', 'Traditional Baklava', 'cat_desserts_001', 7.99,
 'Layers of filo pastry filled with nuts and sweetened with honey syrup',
 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1551024506-0bccd828d307?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Filo Pastry", "price": 2.00}, {"name": "Walnuts", "price": 2.50}, {"name": "Pistachios", "price": 1.50}, {"name": "Butter", "price": 1.00}, {"name": "Honey Syrup", "price": 1.00}]',
 '[]',
 '[{"name": "Extra Honey", "price": 0.50}]',
 '[{"name": "Pistachio Topping", "price": 1.00}, {"name": "Ice Cream", "price": 2.00}]',
 '{"size": ["1 Piece", "2 Pieces", "Box of 6"], "nuts": ["Walnuts", "Pistachios", "Mixed"]}',
 4.7, 67, 198, '2.1 km', '15-20 min', NOW(), NOW()),

('prod_knaffe_001', 'Knafeh', 'cat_desserts_001', 8.99,
 'Sweet cheese pastry soaked in sugar syrup with pistachio topping',
 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1551024506-0bccd828d307?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1572441713132-fb8d9a3e3f1e?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Kadaifi Noodles", "price": 2.50}, {"name": "Cheese", "price": 2.00}, {"name": "Butter", "price": 1.00}, {"name": "Sugar Syrup", "price": 1.50}, {"name": "Pistachios", "price": 1.00}]',
 '[]',
 '[{"name": "Extra Syrup", "price": 0.50}]',
 '[{"name": "Cream", "price": 1.50}, {"name": "Ice Cream", "price": 2.00}]',
 '{"size": ["Small", "Medium", "Large"], "topping": ["Pistachios", "Cream", "Both"]}',
 4.8, 89, 245, '2.1 km', '15-20 min', NOW(), NOW());

-- DRINKS
INSERT INTO products (id, name, category_id, price, description, image, images, status, is_available, main_components, spicy_elements, additional_flavor, optional_add_ons, customization_options, rating, reviews_count, order_count, distance, delivery_time, created_at, updated_at) VALUES
('prod_jallab_001', 'Jallab', 'cat_drinks_001', 4.99,
 'Traditional Middle Eastern drink made with carob molasses and pine nuts',
 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1544145945-f90425340c7e?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Carob Molasses", "price": 1.50}, {"name": "Water", "price": 0.10}, {"name": "Pine Nuts", "price": 1.00}, {"name": "Rose Water", "price": 0.50}, {"name": "Ice", "price": 0.20}]',
 '[]',
 '[{"name": "Extra Pine Nuts", "price": 1.00}]',
 '[{"name": "Lemon", "price": 0.30}, {"name": "Mint", "price": 0.40}]',
 '{"size": ["Small", "Medium", "Large"], "temperature": ["Cold", "Room Temperature"], "sweetness": ["Regular", "Less Sweet", "Extra Sweet"]}',
 4.3, 45, 167, '2.1 km', '5-10 min', NOW(), NOW()),

('prod_lemonade_001', 'Fresh Lemonade', 'cat_drinks_001', 3.99,
 'Freshly squeezed lemonade with mint',
 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1544145945-f90425340c7e?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Fresh Lemons", "price": 1.00}, {"name": "Sugar", "price": 0.50}, {"name": "Water", "price": 0.10}, {"name": "Mint", "price": 0.30}, {"name": "Ice", "price": 0.20}]',
 '[]',
 '[{"name": "Extra Mint", "price": 0.40}]',
 '[{"name": "Ginger", "price": 0.50}, {"name": "Honey", "price": 0.80}]',
 '{"size": ["Small", "Medium", "Large"], "sweetness": ["Regular", "Less Sweet", "Extra Sweet"], "temperature": ["Cold", "Room Temperature"]}',
 4.5, 123, 345, '2.1 km', '5-10 min', NOW(), NOW()),

('prod_ayran_001', 'Ayran', 'cat_drinks_001', 3.49,
 'Traditional Turkish yogurt drink',
 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1544145945-f90425340c7e?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1529006557810-27490341240f?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Yogurt", "price": 1.00}, {"name": "Water", "price": 0.10}, {"name": "Salt", "price": 0.05}, {"name": "Ice", "price": 0.20}]',
 '[]',
 '[{"name": "Mint", "price": 0.30}]',
 '[{"name": "Cucumber", "price": 0.50}, {"name": "Dill", "price": 0.40}]',
 '{"size": ["Small", "Medium", "Large"], "temperature": ["Cold", "Room Temperature"]}',
 4.1, 67, 189, '2.1 km', '5-10 min', NOW(), NOW());

-- FAMILY DEALS
INSERT INTO products (id, name, category_id, price, description, image, images, status, is_available, main_components, spicy_elements, additional_flavor, optional_add_ons, customization_options, rating, reviews_count, order_count, distance, delivery_time, created_at, updated_at) VALUES
('prod_family_deal_001', 'Family Shawarma Feast', 'cat_family_deals_001', 49.99,
 'Serves 4-6 people: Mixed shawarma, rice, salad, hummus, baklava, and drinks',
 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1544124499-58912cbddaad?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "Mixed Shawarma (Chicken & Beef)", "price": 25.00}, {"name": "Rice", "price": 3.00}, {"name": "Salad", "price": 2.00}, {"name": "Hummus", "price": 3.00}, {"name": "Pita Bread", "price": 2.00}, {"name": "Baklava", "price": 5.00}, {"name": "Soft Drinks", "price": 4.00}]',
 '["Medium"]',
 '[{"name": "Extra Protein", "price": 8.00}, {"name": "Extra Baklava", "price": 4.00}]',
 '[{"name": "Hot Sauce", "price": 0.50}, {"name": "Tahini", "price": 1.00}]',
 '{"servings": ["4 People", "6 People"], "protein": ["Chicken", "Beef", "Mixed"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.6, 34, 89, '2.1 km', '30-35 min', NOW(), NOW()),

('prod_family_deal_002', 'Weekend Special Deal', 'cat_family_deals_001', 39.99,
 'Serves 3-4 people: Shawarma wraps, appetizers, and desserts',
 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500&h=400&fit=crop',
 '["https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500&h=400&fit=crop", "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=500&h=400&fit=crop"]',
 'Available', true,
 '[{"name": "4 Shawarma Wraps", "price": 20.00}, {"name": "Falafel", "price": 4.00}, {"name": "Hummus", "price": 3.00}, {"name": "Fries", "price": 3.00}, {"name": "Baklava", "price": 4.00}, {"name": "Soft Drinks", "price": 3.00}]',
 '["Medium"]',
 '[{"name": "Extra Wraps", "price": 5.00}, {"name": "Extra Desserts", "price": 3.00}]',
 '[{"name": "Hot Sauce", "price": 0.50}, {"name": "Tahini", "price": 1.00}]',
 '{"servings": ["3 People", "4 People"], "protein": ["Chicken", "Beef", "Mixed"], "spiceLevel": ["Mild", "Medium", "Hot"]}',
 4.4, 23, 67, '2.1 km', '25-30 min', NOW(), NOW());

-- =============================================
-- VERIFICATION QUERIES
-- =============================================

-- Check categories
SELECT COUNT(*) as total_categories FROM categories;

-- Check products
SELECT COUNT(*) as total_products FROM products;

-- Check products by category
SELECT c.name as category, COUNT(p.id) as product_count
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name
ORDER BY c.name;

-- Check sample product details
SELECT p.name, p.price, c.name as category, p.rating, p.order_count
FROM products p
JOIN categories c ON p.category_id = c.id
ORDER BY p.price DESC
LIMIT 5;

-- =============================================
-- END OF SCRIPT
-- =============================================
