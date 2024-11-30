from geopy.geocoders import Nominatim

def get_address_from_lat_lon(latitude, longitude, timeout=10):
    """
    Get the address from latitude and longitude using reverse geocoding,
    with a configurable timeout to avoid ReadTimeoutError.
    """
    try:
        geolocator = Nominatim(user_agent="geoapi", timeout=timeout)  # Set a longer timeout
        location = geolocator.reverse((latitude, longitude))
        return location.address if location else "Address not found"
    except Exception as e:
        print(f"Error fetching address: {e}")
        return f"Error: {e}"