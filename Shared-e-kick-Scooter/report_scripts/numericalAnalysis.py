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

    def compute_all_results(self, base_distance=1.0, base_locations=5, 
                          distance_range=(0.5, 2.0), distance_steps=5,
                          location_range=(1, 20), location_steps=20):
        """
        Compute results for:
        1. Varying distance with fixed locations
        2. Varying locations with fixed distance
        """
        distance_results = []
        location_results = []
        
        # 1. Vary distance, keep locations constant
        distances = [base_distance + (distance_range[1] - distance_range[0]) * i / distance_steps 
                    for i in range(distance_steps)]
        
        for dist in distances:
            self.DISTANCE_THRESHOLD = dist
            self.NUM_LOCATIONS = base_locations
            self.preprocess_data()  # Recompute coverage matrix with new distance
            result = self.optimize_locations()
            distance_results.append({
                'distance': dist,
                'locations': base_locations,
                'results': result
            })

        # 2. Vary locations, keep distance constant
        self.DISTANCE_THRESHOLD = base_distance
        location_counts = range(location_range[0], location_range[1] + 1, 
                              max(1, (location_range[1] - location_range[0]) // location_steps))
        
        for locs in location_counts:
            self.NUM_LOCATIONS = locs
            self.preprocess_data()
            result = self.optimize_locations()
            location_results.append({
                'distance': base_distance,
                'locations': locs,
                'results': result
            })

        return distance_results, location_results

    def format_results_tables(self, distance_results, location_results):
        """Create formatted tables for both analyses"""
        
        def create_table(results, varying_param_name):
            headers = [varying_param_name, 'Population', 'Bus Access', 'Metro Access', 'POI Coverage']
            rows = []
            
            for result in results:
                param_value = result['distance'] if varying_param_name == 'Distance' else result['locations']
                row = [
                    f"{param_value:.2f}" if varying_param_name == 'Distance' else param_value,
                    f"{result['results']['population_coverage']['objective_value']:.2f}",
                    f"{result['results']['bus_accessibility']['objective_value']:.2f}",
                    f"{result['results']['metro_accessibility']['objective_value']:.2f}",
                    f"{result['results']['poi_coverage']['objective_value']:.2f}"
                ]
                rows.append(row)
            
            return tabulate(rows, headers=headers, tablefmt='grid')

        distance_table = create_table(distance_results, 'Distance')
        location_table = create_table(location_results, 'Locations')
        
        return distance_table, location_table

    def plot_results(self, distance_results, location_results):
        """Plot the results for all objective functions with separate graphs"""
        objectives = ['population_coverage', 'bus_accessibility', 
                    'metro_accessibility', 'poi_coverage']
        
        # Plot distance variation results
        plt.figure(figsize=(15, 10))
        for i, obj in enumerate(objectives, 1):
            plt.subplot(2, 2, i)
            distances = [r['distance'] for r in distance_results]
            values = [r['results'][obj]['objective_value'] for r in distance_results]
            plt.plot(distances, values, 'b-', label='Distance variation')
            plt.xlabel('Distance (km)')
            plt.ylabel('Objective Value')
            plt.title(f'{obj.replace("_", " ").title()}')
            plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot location variation results with star markers
        plt.figure(figsize=(15, 10))
        for i, obj in enumerate(objectives, 1):
            plt.subplot(2, 2, i)
            locations = [r['locations'] for r in location_results]
            values = [r['results'][obj]['objective_value'] for r in location_results]
            
            # Plot line
            plt.plot(locations, values, 'r-', label='Location variation')
            
            # Add star markers
            plt.plot(locations, values, '*', color='black', markersize=8, 
                    label='Zone centroids')
            
            plt.xlabel('Number of Locations')
            plt.ylabel('Objective Value')
            plt.title(f'{obj.replace("_", " ").title()}')
            plt.grid(True)
            plt.legend()
        plt.tight_layout()
        plt.show()

def numericalAnalysisRes(data_file):
    optimizer = EScooterLocationOptimizer(data_file)
    
    # Run analysis with custom ranges
    distance_results, location_results = optimizer.compute_all_results(
        base_distance=0.01,
        base_locations=5,
        distance_range=(0.01, 5.0),
        distance_steps=500,
        location_range=(1, 20),
        location_steps=20
    )
    
    # Generate and print tables
    distance_table, location_table = optimizer.format_results_tables(
        distance_results, location_results
    )
    
    print("Results for varying distance (fixed locations = 5):")
    print(distance_table)
    print("\nResults for varying locations (fixed distance = 0.01 km):")
    print(location_table)
    
    # Plot results
    optimizer.plot_results(distance_results, location_results)