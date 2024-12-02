import json
from geopy.distance import geodesic
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


def calculate_distances(database_path):
    """
    Calculates the distance of each POI, bus station, and metro station to the center of its neighborhood.

    Parameters:
        database_path (str): Path to the input JSON file.

    Returns:
        None
    """
    # Load the JSON data
    with open(database_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Calculate distance_to_center for each neighborhood
    for neighborhood in data:
        if "latitude" in neighborhood and "longitude" in neighborhood:
            center_coords = (neighborhood["latitude"], neighborhood["longitude"])

            for key in ["pois", "bus_stations", "metro_stations"]:
                if key in neighborhood:
                    for item in neighborhood[key]:
                        # Ensure item has latitude and longitude
                        if "latitude" in item and "longitude" in item:
                            item_coords = (item["latitude"], item["longitude"])
                            # Calculate distance and update item
                            item["distance_to_center"] = geodesic(item_coords, center_coords).kilometers

    # Save the updated JSON
    with open(database_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
