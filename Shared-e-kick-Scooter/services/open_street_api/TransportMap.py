from OSMPythonTools.nominatim import Nominatim
import folium
import requests


class TransportMap:
    def __init__(self, location_name, overpass_url="https://overpass-api.de/api/interpreter", radius_km=5):
        self.nominatim = Nominatim()
        self.overpass_url = overpass_url
        self.location_name = location_name
        self.radius_km = radius_km
        self.location = self._get_location()
        self.map = self._initialize_map()
        self.bounding_box = self._define_bounding_box()
        self.all_markers = []  # Track all markers added to this map

    def _get_location(self):
        location = self.nominatim.query(self.location_name)
        lat, lon = location.toJSON()[0]['lat'], location.toJSON()[0]['lon']
        return float(lat), float(lon)

    def _initialize_map(self):
        lat, lon = self.location
        return folium.Map(location=[lat, lon], zoom_start=13)

    def _define_bounding_box(self):
        lat, lon = self.location
        delta = self.radius_km * 0.009  # approximate degrees for 1km
        south = lat - delta
        north = lat + delta
        west = lon - delta
        east = lon + delta
        return south, west, north, east

    def add_search_area_circle(self):
        """
        Add a search area circle around the center location of this map.
        """
        circle = folium.Circle(
            location=self.location,
            radius=self.radius_km * 1000,  # Convert km to meters
            color="red",
            fill=True,
            opacity=0.1,
            popup=f"Search Area ({self.location_name}, {self.radius_km}km radius)"
        )
        circle.add_to(self.map)

    def add_transport_stops(self, stop_type, color, icon, poi_type=None):
        """
        Add transport stops to the map (bus, metro, or POI).
        """
        query = self._create_overpass_query(stop_type, poi_type)
        data = self._query_overpass(query)
        stops = self._add_markers(data, color, icon, stop_type.capitalize())
        self.all_markers.extend(stops)  # Store all added stops
        return stops

    def _create_overpass_query(self, stop_type, poi_type=None):
        """
        Create an Overpass API query based on the stop type.
        """
        south, west, north, east = self.bounding_box
        if stop_type == "bus":
            return f"""
                [out:json];
                (
                    node["highway"="bus_stop"]({south},{west},{north},{east});
                    node["amenity"="bus_station"]({south},{west},{north},{east});
                );
                out body;
            """
        elif stop_type == "metro":
            return f"""
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
        elif stop_type == "poi" and poi_type:
            return f"""
                [out:json];
                (
                    node["amenity"="{poi_type}"]({south},{west},{north},{east});
                );
                out body;
            """
        else:
            raise ValueError("Unsupported stop type or POI type missing")

    def _query_overpass(self, query):
        """
        Perform a query to the Overpass API.
        """
        response = requests.get(self.overpass_url, params={'data': query})
        response.raise_for_status()
        return response.json()

    def _add_markers(self, data, color, icon, location_type):
        """
        Add markers to the map and return a list of stops.
        """
        stops = []
        if 'elements' in data:
            for element in data['elements']:
                popup_info = (
                    f"<b>{location_type}</b><br>"
                    f"Name: {element.get('tags', {}).get('name', 'N/A')}<br>"
                    f"Type: {element.get('tags', {}).get('amenity', element.get('tags', {}).get('railway', 'N/A'))}<br>"
                    f"Operator: {element.get('tags', {}).get('operator', 'N/A')}"
                )
                marker = folium.Marker(
                    [element['lat'], element['lon']],
                    popup=popup_info,
                    tooltip=element.get('tags', {}).get('name', location_type),
                    icon=folium.Icon(color=color, icon=icon),
                )
                marker.add_to(self.map)
                stop_info = {
                    "name": element.get('tags', {}).get('name', 'N/A'),
                    "latitude": element['lat'],
                    "longitude": element['lon'],
                    "distance_to_center": 0  # Placeholder for distance
                }
                stops.append(stop_info)
        return stops

    def merge_map(self, other_map):
        """
        Merge markers and search areas from another TransportMap instance.
        """
        # Add all markers from the other map
        for stop in other_map.all_markers:
            popup_info = (
                f"<b>Stop</b><br>"
                f"Name: {stop['name']}<br>"
                f"Lat: {stop['latitude']}, Lon: {stop['longitude']}"
            )
            marker = folium.Marker(
                [stop['latitude'], stop['longitude']],
                popup=popup_info,
                icon=folium.Icon(color="blue", icon="info-sign")
            )
            marker.add_to(self.map)
            self.all_markers.append(stop)  # Keep track of merged markers

        # Add the search area circle from the other map
        folium.Circle(
            location=other_map.location,
            radius=other_map.radius_km * 1000,
            color="blue",  # Distinguish with another color
            fill=True,
            opacity=0.2,
            popup=f"Search Area ({other_map.location_name}, {other_map.radius_km}km radius)"
        ).add_to(self.map)

    def save_map(self, filename="transport_map.html"):
        """
        Save the current state of the map to an HTML file.
        """
        self.map.save(filename)
        print(f"Map has been generated and saved as '{filename}'")

