import pandas as pd
import json

from services.nominatim.Nominatim import get_address_from_lat_lon


# BaseInfo Interface and Derived Classes
class BaseInfo:
    def __init__(self, name=None, long=None, land=None, distance_to_center=None):
        self.name = name
        self.long = long
        self.land = land
        self.distance_to_center = distance_to_center


class POI(BaseInfo):
    def __init__(self, name=None, long=None, land=None, distance_to_center=None, poi_type=None):
        super().__init__(name, long, land, distance_to_center)
        self.poi_type = poi_type


class BusStation(BaseInfo):
    pass


class MetroStation(BaseInfo):
    pass


# Step 1: Generate JSON with all values initialized to None
def initialize_json(output_file):
    """
    Create an initial JSON structure with all values set to None or empty.
    """
    data = [
        {
            "neighbourhood": None,
            "latitude": None,
            "longitude": None,
            "population": None,
            "poi_number": 0,
            "pois": [],
            "bus_station_number": 0,
            "bus_stations": [],
            "metro_station_number": 0,
            "metro_stations": []
        }
    ]

    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Initial JSON created: {output_file}")

def generate_json_and_map(json_file, transport_map, stop_type, color, icon, poi_type=None):
    """
    Update the bus stop values in the JSON file with data from the TransportMap.

    Parameters:
        json_file (str): Path to the JSON file to update.
        transport_map (TransportMap): Instance of TransportMap to fetch bus stop data.
        stop_type (str): Bus Metro Or POI.
        color (str): Color of the icon.
        icon (str): Icon of the icon .
        poi_type (str): Type of poi (POI).
    """
    if stop_type != "bus" and stop_type != "metro" and stop_type != "poi":
        print("Wrong parameter in generate_json_and_map function")
    try:
        # Load the existing JSON file
        with open(json_file, "r", encoding="utf-8") as f:
            neighborhood_data = json.load(f)

        # Fetch bus stops from the transport map
        stops = transport_map.add_transport_stops(stop_type, color, icon,  poi_type)  # Returns bus stop data
        # Update the JSON with bus stop data
        for neighborhood in neighborhood_data:
            relevant_stops = []
            step = 0
            for stop in stops:
                latitude = stop["latitude"]
                longitude = stop["longitude"]
                if poi_type is not None:
                    stop['poi_type'] = poi_type
                # Get the address for the bus stop
                address = get_address_from_lat_lon(latitude, longitude)
                if address:
                    # Match the neighborhood from address with the neighborhood in the JSON
                    print("------------------STEP------------------")
                    print(step)
                    print("address {}".format(address))
                    # Extract the neighborhood from the address (assume the neighborhood is in the address)
                    neighborhood_name_from_address = address.split(",")[
                        -6].strip()  # Extract the 4th part (adjust if needed)
                    neighborhood_name_from_address = neighborhood_name_from_address.split(" ")[0]
                    print("neighborhood_name_from_address {}".format(neighborhood_name_from_address))
                    if neighborhood_name_from_address.upper() in neighborhood["neighbourhood"].upper():
                        print("matched")
                        print("neighborhood")
                        print(neighborhood)
                        relevant_stops.append(stop)
                    else:
                        print("not matched")
                        print("neighborhood")
                        print(neighborhood)
                    print("-------------------------------------")
                    step += 1
            # Update the neighborhood with relevant bus stops
            print("relevant_stops")
            print(relevant_stops)
            if stop_type == "bus":
                neighborhood["bus_station_number"] = len(relevant_stops)
                neighborhood["bus_stations"] = relevant_stops
            elif stop_type == "metro":
                neighborhood["metro_station_number"] = len(relevant_stops)
                neighborhood["metro_stations"] = relevant_stops
            elif stop_type == "poi":
                neighborhood["poi_number"] = len(relevant_stops)
                neighborhood["pois"] = relevant_stops
            print("neighborhood")
            print(neighborhood)
        # Save the updated JSON file
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(neighborhood_data, f, ensure_ascii=False, indent=4)

        print(f"Stops added and JSON updated: {json_file}")

    except Exception as e:
        print(f"An error occurred while updating bus stops: {str(e)}")
