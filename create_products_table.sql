-- SQL Script for Products Table
-- Only 4 fields are required: image, price, name, description
-- All other fields are optional

CREATE TABLE IF NOT EXISTS products (
    -- Primary Key
    id VARCHAR(36) PRIMARY KEY,

    -- Required Fields (NOT NULL)
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    image VARCHAR(500) NOT NULL,  -- Main product image URL/path
    description TEXT NOT NULL,

    -- Optional Fields (NULL allowed)
    category_id VARCHAR(36) NULL,
    images JSON NULL,  -- Array of additional image URLs
    status VARCHAR(50) DEFAULT 'Available' NULL,
    is_available BOOLEAN DEFAULT TRUE NULL,

    -- Product Components (Optional JSON fields)
    main_components JSON NULL,  -- Array of {name: str, price?: float}
    spicy_elements JSON NULL,   -- Array of strings
    additional_flavor JSON NULL, -- Array of {name: str, price: float}
    optional_add_ons JSON NULL,  -- Array of {name: str, price: float}
    customization_options JSON NULL, -- For breadType, filling, sides, sauces, spiceLevel

    -- Analytics/Stats (Optional)
    rating DECIMAL(3,2) DEFAULT 0.0 NULL CHECK (rating >= 0 AND rating <= 5),
    reviews_count INT DEFAULT 0 NULL,
    order_count INT DEFAULT 0 NULL,

    -- Location/Delivery Info (Optional)
    distance VARCHAR(50) NULL,  -- e.g., "1.5 km"
    delivery_time VARCHAR(50) NULL, -- e.g., "30-40 min"

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes for performance
    INDEX idx_name (name),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_available (is_available),
    INDEX idx_price (price),

    -- Foreign Key (optional relationship)
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Sample INSERT statements with only required fields
INSERT INTO products (id, name, price, image, description) VALUES
('prod_001', 'Chicken Shawarma', 250.00, 'https://example.com/images/chicken-shawarma.jpg', 'Delicious grilled chicken shawarma with traditional spices'),
('prod_002', 'Beef Shawarma', 300.00, 'https://example.com/images/beef-shawarma.jpg', 'Tender beef shawarma marinated in special herbs'),
('prod_003', 'Vegetable Shawarma', 200.00, 'https://example.com/images/veg-shawarma.jpg', 'Healthy vegetable shawarma with fresh veggies and hummus');

-- Sample INSERT with all optional fields filled
INSERT INTO products (
    id, name, price, image, description,
    category_id, images, status, is_available,
    main_components, spicy_elements, rating, reviews_count
) VALUES (
    'prod_004',
    'Family Deal Shawarma',
    800.00,
    'https://example.com/images/family-deal.jpg',
    'Complete family meal with 4 shawarmas, fries, and drinks',
    'cat_001',
    '["https://example.com/images/family-deal-1.jpg", "https://example.com/images/family-deal-2.jpg"]',
    'Available',
    TRUE,
    '[{"name": "Chicken Shawarma", "price": 200}, {"name": "Beef Shawarma", "price": 250}]',
    '["Hot Sauce", "Spicy Mayo"]',
    4.5,
    25
);
