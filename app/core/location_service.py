import requests
import json
import time
import hashlib
from typing import Dict, Optional, Any, Tuple
from functools import lru_cache
from app.core.config import settings

class LocationServiceError(Exception):
    """Custom exception for location service errors"""
    pass

class GoogleMapsService:
    """Google Maps API service with caching and error handling"""

    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.cache_enabled = settings.LOCATION_CACHE_ENABLED
        self.cache_ttl = settings.LOCATION_CACHE_TTL
        self.rate_limit = settings.LOCATION_RATE_LIMIT

        # Simple in-memory cache (in production, use Redis)
        self._cache: Dict[str, Tuple[Any, float]] = {}

        if not self.api_key:
            raise LocationServiceError("Google Maps API key not configured")

    def _get_cache_key(self, operation: str, **params) -> str:
        """Generate cache key from operation and parameters"""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(f"{operation}:{param_str}".encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if still valid"""
        if not self.cache_enabled:
            return None

        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        return None

    def _set_cached_result(self, cache_key: str, result: Any):
        """Cache the result"""
        if self.cache_enabled:
            self._cache[cache_key] = (result, time.time())

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Google Maps API with error handling"""
        url = f"{self.base_url}/{endpoint}"
        params['key'] = self.api_key

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check for Google API errors
                if data.get('status') == 'OK':
                    return data
                elif data.get('status') == 'ZERO_RESULTS':
                    raise LocationServiceError("No results found for the given location")
                elif data.get('status') == 'OVER_QUERY_LIMIT':
                    raise LocationServiceError("Google Maps API quota exceeded")
                elif data.get('status') == 'REQUEST_DENIED':
                    raise LocationServiceError("Google Maps API request denied - check API key")
                elif data.get('status') == 'INVALID_REQUEST':
                    raise LocationServiceError("Invalid request parameters")
                else:
                    raise LocationServiceError(f"Google Maps API error: {data.get('status', 'Unknown error')}")

            elif response.status_code == 403:
                raise LocationServiceError("Google Maps API access forbidden - check API key permissions")
            elif response.status_code == 429:
                raise LocationServiceError("Google Maps API rate limit exceeded")
            else:
                raise LocationServiceError(f"HTTP {response.status_code}: {response.text}")

        except requests.RequestException as e:
            raise LocationServiceError(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            raise LocationServiceError("Invalid response from Google Maps API")

    def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Convert coordinates to address (reverse geocoding)

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dict containing address information
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise LocationServiceError("Invalid latitude. Must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise LocationServiceError("Invalid longitude. Must be between -180 and 180")

        cache_key = self._get_cache_key('reverse_geocode', lat=latitude, lng=longitude)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result

        # Make API request
        response = self._make_request("geocode/json", {
            'latlng': f"{latitude},{longitude}",
            'language': 'en'
        })

        # Parse response
        if not response.get('results'):
            raise LocationServiceError("No address found for these coordinates")

        result = response['results'][0]  # Get the first (most relevant) result

        # Extract components
        address_components = result.get('address_components', [])
        components = {}

        for component in address_components:
            types = component.get('types', [])
            if 'street_number' in types:
                components['street_number'] = component['long_name']
            elif 'route' in types:
                components['street'] = component['long_name']
            elif 'locality' in types or 'administrative_area_level_2' in types:
                components['city'] = component['long_name']
            elif 'administrative_area_level_1' in types:
                components['state'] = component['long_name']
            elif 'country' in types:
                components['country'] = component['long_name']
            elif 'postal_code' in types:
                components['postalCode'] = component['long_name']

        # Build full address
        formatted_address = result.get('formatted_address', '')

        result_data = {
            'address': formatted_address.split(',')[0] if ',' in formatted_address else formatted_address,
            'formattedAddress': formatted_address,
            'components': components,
            'latitude': latitude,
            'longitude': longitude,
            'placeId': result.get('place_id'),
            'types': result.get('types', [])
        }

        self._set_cached_result(cache_key, result_data)
        return result_data

    def geocode(self, address: str) -> Dict[str, Any]:
        """
        Convert address to coordinates (geocoding)

        Args:
            address: Address string to geocode

        Returns:
            Dict containing coordinate and address information
        """
        if not address or not address.strip():
            raise LocationServiceError("Address is required")

        address = address.strip()
        cache_key = self._get_cache_key('geocode', address=address)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result

        # Make API request
        response = self._make_request("geocode/json", {
            'address': address,
            'language': 'en'
        })

        # Parse response
        if not response.get('results'):
            raise LocationServiceError("No coordinates found for this address")

        result = response['results'][0]  # Get the first (most relevant) result
        location = result['geometry']['location']

        result_data = {
            'address': address,
            'latitude': location['lat'],
            'longitude': location['lng'],
            'formattedAddress': result.get('formatted_address', address),
            'placeId': result.get('place_id'),
            'types': result.get('types', [])
        }

        self._set_cached_result(cache_key, result_data)
        return result_data

    def get_distance_matrix(self, origins: list, destinations: list, mode: str = 'driving') -> Dict[str, Any]:
        """
        Calculate distance and duration between multiple points

        Args:
            origins: List of origin addresses or coordinates
            destinations: List of destination addresses or coordinates
            mode: Travel mode ('driving', 'walking', 'bicycling', 'transit')

        Returns:
            Distance matrix data
        """
        if not origins or not destinations:
            raise LocationServiceError("Origins and destinations are required")

        cache_key = self._get_cache_key('distance_matrix',
                                       origins=origins,
                                       destinations=destinations,
                                       mode=mode)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result

        # Convert coordinates to strings if needed
        def format_location(loc):
            if isinstance(loc, dict) and 'lat' in loc and 'lng' in loc:
                return f"{loc['lat']},{loc['lng']}"
            return str(loc)

        origins_str = '|'.join([format_location(loc) for loc in origins])
        destinations_str = '|'.join([format_location(loc) for loc in destinations])

        response = self._make_request("distancematrix/json", {
            'origins': origins_str,
            'destinations': destinations_str,
            'mode': mode,
            'units': 'metric'
        })

        self._set_cached_result(cache_key, response)
        return response

# Global service instance
_google_maps_service: Optional[GoogleMapsService] = None

def get_google_maps_service() -> GoogleMapsService:
    """Get or create Google Maps service instance"""
    global _google_maps_service
    if _google_maps_service is None:
        _google_maps_service = GoogleMapsService()
    return _google_maps_service
