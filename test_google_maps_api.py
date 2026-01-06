#!/usr/bin/env python3
"""
Test script to verify Google Maps API integration and identify which API key works
"""
import requests
import sys

def test_google_maps_api_key(api_key, key_name):
    """Test if an API key works with Google Maps API"""
    print(f"\n[*] Testing {key_name}: {api_key[:20]}...")

    # Test 1: Reverse Geocoding (coordinates to address)
    print("  [-] Testing Reverse Geocoding...")
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'latlng': '31.5204,74.3587',  # Lahore coordinates
            'key': api_key
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get('status') == 'OK':
            print("    [+] Reverse Geocoding: SUCCESS")
            print(f"    [-] Address: {data['results'][0]['formatted_address'][:50]}...")
            return True
        else:
            print(f"    [-] Reverse Geocoding: FAILED - Status: {data.get('status')}")
            if 'error_message' in data:
                print(f"    [!] Error: {data['error_message']}")
            return False

    except Exception as e:
        print(f"    [-] Reverse Geocoding: ERROR - {str(e)}")
        return False

def main():
    """Test both API keys"""
    print("Testing Google Maps API Keys")
    print("=" * 50)

    # API Keys to test
    keys_to_test = [
        ("AIzaSyDmJZKgxWpCABNC86QTLkgh_StWimkrL0Y", "GEMINI_API_KEY"),
        ("AIzaSyC0jciSBGchQc1NdVV4huzCWdCXWn_O-bY", "STT_API_KEY")
    ]

    working_keys = []

    for api_key, key_name in keys_to_test:
        if test_google_maps_api_key(api_key, key_name):
            working_keys.append((api_key, key_name))

    print("\n" + "=" * 50)
    print("RESULTS:")

    if working_keys:
        for api_key, key_name in working_keys:
            print(f"[+] {key_name}: WORKS with Google Maps API")
            print("   Add to .env file:")
            print(f"   GOOGLE_MAPS_API_KEY={api_key}")
    else:
        print("[-] No API key works with Google Maps API")
        print("Make sure to enable Geocoding API in Google Cloud Console")

    print("\nAdditional Environment Variables to add:")
    print("LOCATION_CACHE_ENABLED=true")
    print("LOCATION_CACHE_TTL=3600")
    print("LOCATION_RATE_LIMIT=100")

if __name__ == "__main__":
    main()
