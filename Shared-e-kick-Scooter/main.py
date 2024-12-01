import sys
from services.election_api.ElectionResult import process_population_data
from services.json_api.JSONManipulation import initialize_json, generate_json_and_map
from services.open_street_api.TransportMap import TransportMap

if __name__ == "__main__":
    input_file = "database/input/kadikoy.xlsx"
    output_file = "database/output/database.json"

    print('The command line arguments are:')
    for i in sys.argv:
        print(i)

    if len(sys.argv) == 3:
        if sys.argv[1] == "-updateAll":
            # Initialize JSON
            initialize_json(output_file)

            # Process population data
            process_population_data(input_file, output_file)

        try:
            # Create a TransportMap instance and fetch transport data
            transport_map = TransportMap("Kadıkoy, Istanbul, Turkey")
            transport_map.add_search_area_circle()

            # Update JSON and map with bus stop data
            if sys.argv[1] == "-updateAll" or sys.argv[1] == "-updateBusStops":
                generate_json_and_map(output_file, transport_map, "bus", "blue", "info-sign")
            # Update JSON and map with metro stop data

            elif sys.argv[1] == "-updateAll" or sys.argv[1] == "-updateMetroStops":
                generate_json_and_map(output_file, transport_map, "metro", "purple", "info-sign")

            # Update JSON and map with POI points data
            elif sys.argv[1] == "-updateAll" or sys.argv[1] == "-updatePoiPoints":
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="taxi")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign", poi_type="fast_food")
            else:
                print("Wrong Parameter")
                exit()
            # Save the map (optional)
            if len(sys.argv) == 3 and sys.argv[2] == "-enableMapUpdate":
                transport_map.save_map("kadikoy_transport_map.html")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    else:
        print("\nInvalid Argument\n"
              "Example: python main.py "
              "Argument 1: <-updateAll | -updateBusStops | -updatePoiPoints | -updateMetroStops | -onlyCplex> \n"
              "Argument 2: <-enableMapUpdate>")