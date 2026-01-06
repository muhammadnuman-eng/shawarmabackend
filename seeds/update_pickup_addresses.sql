-- Update pickup addresses with correct coordinates
-- PostgreSQL SQL Script

-- Update DHA Phase 4 (coordinates same)
UPDATE addresses
SET latitude = 31.4697, longitude = 74.2728, updated_at = NOW()
WHERE id = 'dha-phase-4';

-- Update Main PIA Road (corrected coordinates)
UPDATE addresses
SET latitude = 31.5204, longitude = 74.3587, updated_at = NOW()
WHERE id = 'main-pia-road';

-- Update Lake City (corrected coordinates)
UPDATE addresses
SET latitude = 31.4239, longitude = 74.2542, updated_at = NOW()
WHERE id = 'lake-city';

-- Verify updates
SELECT 'Pickup addresses updated successfully!' as status;

-- Show updated pickup addresses
SELECT
    id,
    name,
    address,
    latitude,
    longitude,
    type
FROM addresses
WHERE type = 'pickup'
ORDER BY name;
