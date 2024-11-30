from services.election_api.ElectionResult import process_population_data
from services.json_api.JSONManipulation import initialize_json
from services.nominatim.Nominatim import get_address_from_lat_lon
from services.open_street_api.TransportMap import TransportMap
import json


def update_bus_stops_in_json(json_file, transport_map):
    """
    Update the bus stop values in the JSON file with data from the TransportMap.

    Parameters:
        json_file (str): Path to the JSON file to update.
        transport_map (TransportMap): Instance of TransportMap to fetch bus stop data.
    """
    try:
        # Load the existing JSON file
        with open(json_file, "r", encoding="utf-8") as f:
            neighborhood_data = json.load(f)

        # Fetch bus stops from the transport map
        bus_stops = transport_map.add_transport_stops("bus", "blue", "info-sign")  # Returns bus stop data
        # Update the JSON with bus stop data
        for neighborhood in neighborhood_data:
            relevant_stops = []
            step = 0
            for stop in bus_stops:
                latitude = stop["latitude"]
                longitude = stop["longitude"]
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
            neighborhood["bus_station_number"] = len(relevant_stops)
            neighborhood["bus_stations"] = relevant_stops
            print("neighborhood")
            print(neighborhood)
        # Save the updated JSON file
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(neighborhood_data, f, ensure_ascii=False, indent=4)

        print(f"Bus stops added and JSON updated: {json_file}")

    except Exception as e:
        print(f"An error occurred while updating bus stops: {str(e)}")


if __name__ == "__main__":
    input_file = "database/input/kadikoy.xlsx"
    output_file = "database/output/database.json"

    # Step 1: Initialize JSON
    initialize_json(output_file)

    # Step 2: Process population data
    process_population_data(input_file, output_file)

    try:
        # Create a TransportMap instance and fetch transport data
        transport_map = TransportMap("Kadıkoy, Istanbul, Turkey")
        transport_map.add_search_area_circle()
        transport_map.add_transport_stops("bus", "blue", "info-sign")

        # Update JSON with bus stop data
        update_bus_stops_in_json(output_file, transport_map)

        # Save the map (optional)
        transport_map.save_map("kadikoy_transport_map.html")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
