import json
import math
import time
import matplotlib.pyplot as plt
from docplex.cp.model import CpoModel
from tabulate import tabulate

class EScooterLocationOptimizer:
    def __init__(self, data_file, distance_threshold=1, num_locations=5):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.zones = json.load(f)
        
        self.DISTANCE_THRESHOLD = distance_threshold  # Dc in kilometers
        self.NUM_LOCATIONS = num_locations  # s in the tables
        self.preprocess_data()

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate the great circle distance between two points on the Earth."""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of Earth in kilometers
        return c * r

    def preprocess_data(self):
        """Preprocess the zone data and compute necessary metrics."""
        self.I = list(range(len(self.zones)))
        self.J = list(range(len(self.zones)))
        self.population = {i: zone.get('population', 0) for i, zone in enumerate(self.zones)}
        self.poi_count = {i: zone.get('poi_number', 0) for i, zone in enumerate(self.zones)}
        self.coverage_matrix = self.compute_coverage_matrix()
        self.bus_accessibility = self.compute_accessibility('bus_stations')
        self.metro_accessibility = self.compute_accessibility('metro_stations')

    def compute_coverage_matrix(self):
        """Compute a coverage matrix based on distance thresholds."""
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
        """Compute accessibility scores for bus or metro stations."""
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
        """Perform multi-objective optimization to select e-scooter locations."""
        results = {}

        objectives = {
            'population_coverage': lambda mdl, yi: mdl.sum(self.population[i] * yi[i] for i in self.I),
            'bus_accessibility': lambda mdl, yi: mdl.sum(self.bus_accessibility[i] * yi[i] for i in self.I),
            'metro_accessibility': lambda mdl, yi: mdl.sum(self.metro_accessibility[i] * yi[i] for i in self.I),
            'poi_coverage': lambda mdl, yi: mdl.sum(self.poi_count[i] * yi[i] for i in self.I),
        }

        for obj_name, obj_func in objectives.items():
            start_time = time.time()

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
            
            end_time = time.time()
            cpu_time = end_time - start_time

            if solution:
                results[obj_name] = {
                    'objective_value': solution.get_objective_value(),
                    'cpu_time': cpu_time
                }

        return results

    def compute_all_results(self, num_steps=5, step_size=0.01):
        """Compute results for varying distance and number of locations."""
        all_results1 = []
        all_results2 = []
        self.DISTANCE_THRESHOLD -= 0.01
        self.NUM_LOCATIONS = 5
        # Vary distance
        for step in range(num_steps):
            self.DISTANCE_THRESHOLD += step_size
            result = self.optimize_locations()
            all_results1.append((self.DISTANCE_THRESHOLD, self.NUM_LOCATIONS, result))
        
        # Reset distance to the original and vary number of locations
        self.DISTANCE_THRESHOLD -= 1
        self.NUM_LOCATIONS = 1
        num_steps=20
        for step in range(num_steps):
            self.NUM_LOCATIONS += 1
            result = self.optimize_locations()
            all_results2.append((self.DISTANCE_THRESHOLD, self.NUM_LOCATIONS, result))

        return all_results1,all_results2

    def plot_results(self, all_results):
        """Plot the results for all objective functions."""
        for obj_name in ['population_coverage', 'bus_accessibility', 'metro_accessibility', 'poi_coverage']:
            distances = []
            locations = []
            objective_values = []

            for distance, num_locations, result in all_results:
                distances.append(distance)
                locations.append(num_locations)
                objective_values.append(result[obj_name]['objective_value'])

            plt.figure(figsize=(10, 6))
            plt.plot(distances, objective_values, label=f"{obj_name} (varying distance)")
            plt.plot(locations, objective_values, label=f"{obj_name} (varying locations)", linestyle='--')
            plt.xlabel('Parameter (Distance or Locations)')
            plt.ylabel('Objective Value')
            plt.title(f"Objective Function: {obj_name}")
            plt.legend()
            plt.grid(True)
            plt.show()

def numericalAnalysisRes(data_file):
    optimizer = EScooterLocationOptimizer(data_file)
    results1, results2 = optimizer.compute_all_results()
    
    # Process results for varying distance (results1)
    for distance, num_locations, result in results1:
        print(f"Distance: {distance:.2f} km, Number of Locations: {num_locations}")
        for obj_name, metrics in result.items():
            print(f"Objective: {obj_name}")
            print(f"  Objective Value: {metrics['objective_value']:.2f}")
            print(f"  CPU Time: {metrics['cpu_time']:.2f}s")
        print("-" * 40)  # Separator line for clarity

    # Process results for varying number of locations (results2)
    for distance, num_locations, result in results2:
        print(f"Distance: {distance:.2f} km, Number of Locations: {num_locations}")
        for obj_name, metrics in result.items():
            print(f"Objective: {obj_name}")
            print(f"  Objective Value: {metrics['objective_value']:.2f}")
            print(f"  CPU Time: {metrics['cpu_time']:.2f}s")
        print("-" * 40)  # Separator line for clarity

    # Plot the results for varying distance and number of locations
    optimizer.plot_results(results1)
    optimizer.plot_results(results2)



