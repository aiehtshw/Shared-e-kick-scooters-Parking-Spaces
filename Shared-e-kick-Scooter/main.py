from services.open_street_api.TransportMap import TransportMap

if __name__ == "__main__":
    try:
        transport_map = TransportMap("Kadıkoy, Istanbul, Turkey")
        transport_map.add_search_area_circle()
        #transport_map.add_transport_stops("bus", "blue", "info-sign")
        #transport_map.add_transport_stops("metro", "purple", "info-sign")

        # Adding points of interest such as restaurants and parks
        #transport_map.add_transport_stops("poi", "green", "info-sign", poi_type="parking_entrance")
        transport_map.add_transport_stops("poi", "green", "info-sign", poi_type="taxi")
        #transport_map.add_transport_stops("poi", "orange", "info-sign", poi_type="park")

        transport_map.save_map("kadikoy_transport_map.html")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
