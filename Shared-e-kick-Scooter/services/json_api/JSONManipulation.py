import pandas as pd
import json


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