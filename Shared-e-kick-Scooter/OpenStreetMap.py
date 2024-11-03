from OSMPythonTools.nominatim import Nominatim
import folium
import requests

# Initialize Nominatim service
nominatim = Nominatim()
overpass_url = "https://overpass-api.de/api/interpreter"

try:
    # Search for Tuzla, Istanbul using Nominatim
    location = nominatim.query('Kadıkoy, Istanbul, Turkey')
    lat, lon = location.toJSON()[0]['lat'], location.toJSON()[0]['lon']

    # Create a folium map centered around Tuzla, Istanbul
    m = folium.Map(location=[float(lat), float(lon)], zoom_start=13)

    # Define a bounding box around Tuzla (approximately 5km radius)
    delta = 0.045  # roughly 5km
    south = float(lat) - delta
    north = float(lat) + delta
    west = float(lon) - delta
    east = float(lon) + delta

    # Define queries
    bus_stops_query = f"""
    [out:json];
    (
        node["highway"="bus_stop"]({south},{west},{north},{east});
        node["amenity"="bus_station"]({south},{west},{north},{east});
    );
    out body;
    """
    
    metro_stations_query = f"""
    [out:json];
    (
        node["railway"="station"]({south},{west},{north},{east});
        node["railway"="stop"]({south},{west},{north},{east});
        node["railway"="subway_entrance"]({south},{west},{north},{east});
        node["railway"="halt"]({south},{west},{north},{east});
        node["public_transport"="station"]({south},{west},{north},{east});
    );
    out body;
    """

    # Make requests to Overpass API
    print("Querying bus stops...")
    bus_stops_response = requests.get(overpass_url, params={'data': bus_stops_query})
    bus_stops_data = bus_stops_response.json()

    print("Querying metro/train stations...")
    metro_stations_response = requests.get(overpass_url, params={'data': metro_stations_query})
    metro_stations_data = metro_stations_response.json()

    # Add circle to show search area
    folium.Circle(
        location=[float(lat), float(lon)],
        radius=5000,  # 5km in meters
        color="red",
        fill=True,
        opacity=0.1,
        popup="Search Area (5km radius)"
    ).add_to(m)

    # Add bus stops to the map
    bus_stop_count = 0
    if 'elements' in bus_stops_data:
        for stop in bus_stops_data['elements']:
            bus_stop_count += 1
            popup_info = (
                f"<b>Bus Stop</b><br>"
                f"Name: {stop.get('tags', {}).get('name', 'N/A')}<br>"
                f"Ref: {stop.get('tags', {}).get('ref', 'N/A')}<br>"
                f"Operator: {stop.get('tags', {}).get('operator', 'N/A')}"
            )
            folium.Marker(
                [stop['lat'], stop['lon']],
                popup=popup_info,
                tooltip=stop.get('tags', {}).get('name', 'Bus Stop'),
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(m)
    print(f"Found {bus_stop_count} bus stops")

    # Add metro/train stations to the map
    station_count = 0
    if 'elements' in metro_stations_data:
        for station in metro_stations_data['elements']:
            station_count += 1
            popup_info = (
                f"<b>Station</b><br>"
                f"Name: {station.get('tags', {}).get('name', 'N/A')}<br>"
                f"Type: {station.get('tags', {}).get('railway', 'N/A')}<br>"
                f"Operator: {station.get('tags', {}).get('operator', 'N/A')}"
            )
            folium.Marker(
                [station['lat'], station['lon']],
                popup=popup_info,
                tooltip=station.get('tags', {}).get('name', 'Station'),
                icon=folium.Icon(color="purple", icon="info-sign"),
            ).add_to(m)
    print(f"Found {station_count} metro/train stations")

    # Add center marker
    folium.Marker(
        [float(lat), float(lon)],
        popup="Tuzla Center",
        tooltip="Tuzla, Istanbul",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    # Save the map
    m.save("tuzla_transport_map.html")
    print("Map has been generated and saved as 'tuzla_transport_map.html'")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    
    # Print more detailed error information if available
    if 'bus_stops_response' in locals():
        print("\nBus stops response status code:", bus_stops_response.status_code)
        print("Bus stops response content:", bus_stops_response.text[:500])
    if 'metro_stations_response' in locals():
        print("\nMetro stations response status code:", metro_stations_response.status_code)
        print("Metro stations response content:", metro_stations_response.text[:500])