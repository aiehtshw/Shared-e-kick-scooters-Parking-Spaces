import sys
from report_scripts.tableRes import tableResult
from services.cplex import execCplex
from services.election_api.ElectionResult import process_population_data
from services.elitistga import execEga
from services.json_api.JSONManipulation import initialize_json, generate_json_and_map
from services.nominatim.Nominatim import calculate_distances
from services.open_street_api.TransportMap import TransportMap

if __name__ == "__main__":

    input_file = "database/input/kadikoy.xlsx"
    output_file = "database/output/database.json"

    if len(sys.argv) == 3 or len(sys.argv) == 2 :
        if sys.argv[1] == "-updateAll":
            # Initialize JSON
            initialize_json(output_file)

            # Process population data
            process_population_data(input_file, output_file)
            

        try:

            transport_map = TransportMap("Kadıkoy, Istanbul, Turkey")
            transport_map1 = TransportMap("19 MAYIS MAHALLESİ, Istanbul, Turkey", radius_km=3)

            # Add search areas
            transport_map.add_search_area_circle()
            transport_map1.add_search_area_circle()

            # Update JSON and map with bus stop data
            if sys.argv[1] == "-updateAll" or sys.argv[1] == "-updateBusStops":
                generate_json_and_map(output_file, transport_map, "bus", "blue", "info-sign")
                generate_json_and_map(output_file, transport_map1, "bus", "blue", "info-sign")
                
            # Update JSON and map with metro stop data

            if sys.argv[1] == "-updateAll" or sys.argv[1] == "-updateMetroStops":
                generate_json_and_map(output_file, transport_map, "metro", "purple", "info-sign")
                generate_json_and_map(output_file, transport_map1, "metro", "purple", "info-sign")
                

            # Update JSON and map with POI points data
            if sys.argv[1] == "-updateAll" or sys.argv[1] == "-updatePoiPoints":
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="taxi")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="taxi")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign", poi_type="fast_food")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign", poi_type="fast_food")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="cafe")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="cafe")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="restaurant")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="restaurant")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="college")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="college")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="library")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="library")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="school")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="school")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="university")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="university")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="atm")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="atm")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="hospital")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="hospital")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="arts_centre")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="arts_centre")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="cinema")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="cinema")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="theatre")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="theatre")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="grave_yard")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="grave_yard")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="social_centre")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="social_centre")
                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="social_facility")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="social_facility")

                
                
                #### OPTIONAL #####

                generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="nightclub")
                generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="nightclub")

                #-generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="bank")
                #-generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="bank")
                #-generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="clinic")
                #-generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="clinic")
                #-generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="dentist")
                #-generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="dentist")
                #-generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="pharmacy")
                #-generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="pharmacy")
                #-generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="post_office")
                #-generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="post_office")
                #-generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="toilets")
                #-generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="toilets")
                #-generate_json_and_map(output_file, transport_map, "poi", "green", "info-sign",  poi_type="baking_oven")
                #-generate_json_and_map(output_file, transport_map1, "poi", "green", "info-sign",  poi_type="baking_oven")
                
            calculate_distances(output_file)

            # CPlex and Elitist GA
            if sys.argv[1] == "-onlyCalculations":
                ##print("run cplex and elitist ga")
                
                execCplex(output_file)
                #execEga(output_file)
            
            # Table of the result of objective functions
            if sys.argv[1] == "-onlyReport":
                tableResult(output_file)


            if not(sys.argv[1] == "-updateAll" or sys.argv[1] == "-updatePoiPoints" or sys.argv[1] == "-updateMetroStops" or sys.argv[1] == "-updateBusStops" or sys.argv[1] == "-onlyCalculations" or sys.argv[1] == "-onlyReport"):
                print("Wrong Parameter")
                exit()


            # Save the map (optional)
            if len(sys.argv) == 3 and sys.argv[2] == "-enableMapUpdate":
                # Merge transport_map1 into transport_map
                transport_map.merge_map(transport_map1)
                # Save the combined map with all markers and search areas
                transport_map.save_map("kadikoy_combined_transport_map.html")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    else:
        print("\nInvalid Argument\n"
              "Example: python main.py "
              "Argument 1: <-updateAll | -updateBusStops | -updatePoiPoints | -updateMetroStops | -onlyCalculations | -onlyReport> \n"
              "Argument 2: <-enableMapUpdate>")