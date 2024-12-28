import json
import math
from docplex.cp.model import CpoModel


class EScooterLocationOptimizer:
    def __init__(self, data_file, distance_threshold=1.0, num_locations=5):
        """
        Initialize the optimizer with configuration parameters.

        Args:
            data_file (str): Path to the JSON data file.
            distance_threshold (float): Maximum distance for coverage (in kilometers).
            num_locations (int): Number of e-scooter locations to select.
        """
        with open(data_file, 'r', encoding='utf-8') as f:
            self.zones = json.load(f)

        self.DISTANCE_THRESHOLD = distance_threshold
        self.NUM_LOCATIONS = num_locations
        self.preprocess_data()

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points on the Earth.
        """
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of Earth in kilometers
        return c * r

    def preprocess_data(self):
        """
        Preprocess the zone data and compute necessary metrics.
        """
        self.I = list(range(len(self.zones)))
        self.J = list(range(len(self.zones)))
        self.population = {i: zone.get('population', 0) for i, zone in enumerate(self.zones)}
        self.poi_count = {i: zone.get('poi_number', 0) for i, zone in enumerate(self.zones)}
        self.coverage_matrix = self.compute_coverage_matrix()
        self.bus_accessibility = self.compute_accessibility('bus_stations')
        self.metro_accessibility = self.compute_accessibility('metro_stations')

    def compute_coverage_matrix(self):
        """
        Compute a coverage matrix based on distance thresholds.
        """
        coverage = {}
        for i in self.I:
            for j in self.J:
                dist = self.haversine_distance(
                    self.zones[i]['latitude'], self.zones[i]['longitude'],
                    self.zones[j]['latitude'], self.zones[j]['longitude']
                )
                coverage[(i, j)] = 1 if dist <= self.DISTANCE_THRESHOLD else 0
        return coverage

    def compute_accessibility(self, station_key):
        """
        Compute accessibility scores for bus or metro stations.
        """
        accessibility = {}
        for i, zone in enumerate(self.zones):
            score = sum(
                math.exp(-station['distance_to_center'])
                for station in zone.get(station_key, [])
                if station.get('distance_to_center', float('inf')) > 0
            )
            accessibility[i] = score
        return accessibility

    def optimize_locations(self):
        """
        Perform multi-objective optimization to select e-scooter locations.
        """
        results = {}

        objectives = {
            'population_coverage': lambda mdl, yi: mdl.sum(self.population[i] * yi[i] for i in self.I),
            'poi_coverage': lambda mdl, yi: mdl.sum(self.poi_count[i] * yi[i] for i in self.I),
            'bus_accessibility': lambda mdl, yi: mdl.sum(self.bus_accessibility[i] * yi[i] for i in self.I),
            'metro_accessibility': lambda mdl, yi: mdl.sum(self.metro_accessibility[i] * yi[i] for i in self.I),
        }

        for obj_name, obj_func in objectives.items():
            # Create a new model for each objective
            mdl = CpoModel(name=f"E-Scooter Optimization - {obj_name}")

            # Decision variables
            xj = mdl.binary_var_dict(self.J, name="location_selection")
            yi = mdl.binary_var_dict(self.I, name="zone_coverage")

            # Add the objective function
            mdl.add(mdl.maximize(obj_func(mdl, yi)))

            # Add coverage constraints
            for i in self.I:
                mdl.add(
                    mdl.if_then(
                        mdl.sum(self.coverage_matrix[(i, j)] * xj[j] for j in self.J) > 0,
                        yi[i] == 1
                    )
                )
                mdl.add(
                    mdl.if_then(
                        mdl.sum(self.coverage_matrix[(i, j)] * xj[j] for j in self.J) == 0,
                        yi[i] == 0
                    )
                )

            # Limit the number of selected locations
            mdl.add(mdl.sum(xj[j] for j in self.J) == self.NUM_LOCATIONS)

            # Solve the model
            solution = mdl.solve()

            if solution:
                results[obj_name] = {
                    'objective_value': solution.get_objective_values()[0],
                    'selected_locations': [j for j in self.J if solution[xj[j]] == 1],
                    'covered_zones': [i for i in self.I if solution[yi[i]] == 1]
                }
            else:
                results[obj_name] = {
                    'objective_value': None,
                    'selected_locations': [],
                    'covered_zones': []
                }

        return results

    def detailed_location_analysis(self, results):
        """
        Provide a detailed analysis of the selected locations.
        """
        analysis = {}
        for obj_name, obj_results in results.items():
            analysis[obj_name] = {
                'Total Objective Value': obj_results['objective_value'],
                'Selected Locations': [
                    {
                        'Zone Index': loc,
                        'Neighbourhood': self.zones[loc]['neighbourhood'],
                        'Latitude': self.zones[loc]['latitude'],
                        'Longitude': self.zones[loc]['longitude'],
                        'Population': self.population[loc],
                        'POI Count': self.poi_count[loc],
                        'Bus Stations': len(self.zones[loc].get('bus_stations', [])),
                        'Metro Stations': len(self.zones[loc].get('metro_stations', []))
                    }
                    for loc in obj_results['selected_locations']
                ],
                'Covered Zones Count': len(obj_results['covered_zones'])
            }
        return analysis


# Main execution
def execCplex(path):
    
    try:
        optimizer = EScooterLocationOptimizer(path)
        optimization_results = optimizer.optimize_locations()
        detailed_analysis = optimizer.detailed_location_analysis(optimization_results)

        print("E-Scooter Location Optimization Results:\n")
        for obj_name, analysis in detailed_analysis.items():
            print(f"Objective: {obj_name}")
            print(f"Total Objective Value: {analysis['Total Objective Value']}")
            print("Selected Locations:")
            for loc in analysis['Selected Locations']:
                print(f"  - Zone: {loc['Neighbourhood']} (Index {loc['Zone Index']})")
                print(f"    Coordinates: ({loc['Latitude']}, {loc['Longitude']})")
                print(f"    Population: {loc['Population']}")
                print(f"    POI Count: {loc['POI Count']}")
                print(f"    Bus Stations: {loc['Bus Stations']}")
                print(f"    Metro Stations: {loc['Metro Stations']}")
            print(f"Total Covered Zones: {analysis['Covered Zones Count']}\n")
    except FileNotFoundError:
        print(f"Error: JSON data file not found at {path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

