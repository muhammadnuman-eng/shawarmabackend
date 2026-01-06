-- Migration Script: Convert menu_items table to products table
-- Makes only 4 fields required: image, price, name, description

-- Step 1: Rename existing table (backup)
ALTER TABLE menu_items RENAME TO menu_items_backup;

-- Step 2: Create new products table with only 4 required fields
CREATE TABLE products (
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

-- Step 3: Migrate data from backup table to new products table
-- Only copy records that have required fields (image, name, price, description)
INSERT INTO products (
    id, name, price, image, description,
    category_id, images, status, is_available,
    main_components, spicy_elements, additional_flavor,
    optional_add_ons, customization_options,
    rating, reviews_count, order_count,
    distance, delivery_time, created_at, updated_at
)
SELECT
    id, name, price, image, description,
    category_id, images, status, is_available,
    main_components, spicy_elements, additional_flavor,
    optional_add_ons, customization_options,
    rating, reviews_count, order_count,
    distance, delivery_time, created_at, updated_at
FROM menu_items_backup
WHERE image IS NOT NULL
  AND name IS NOT NULL
  AND price IS NOT NULL
  AND description IS NOT NULL;

-- Step 4: Show migration results
SELECT
    'Migration completed!' as status,
    (SELECT COUNT(*) FROM menu_items_backup) as total_menu_items,
    (SELECT COUNT(*) FROM products) as migrated_products,
    ((SELECT COUNT(*) FROM menu_items_backup) - (SELECT COUNT(*) FROM products)) as skipped_items;

-- Step 5: Optional - Drop backup table after verification
-- WARNING: Only run this after verifying migration is successful!
-- DROP TABLE menu_items_backup;
