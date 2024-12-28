import json
import math
import time
from docplex.cp.model import CpoModel
from tabulate import tabulate

class EScooterLocationOptimizer:
    def __init__(self, data_file, distance_threshold=1.0, num_locations=5):
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

        case_mapping = {
            'population_coverage': 1,
            'bus_accessibility': 2,
            'metro_accessibility': 3,
            'poi_coverage': 4
        }

        for obj_name, obj_func in objectives.items():
            case_num = case_mapping[obj_name]
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
                covered_zones = [i for i in self.I if solution[yi[i]] == 1]
                selected_locations = [j for j in self.J if solution[xj[j]] == 1]
                
                total_population = sum(self.population.values())
                covered_population = sum(self.population[i] for i in covered_zones)
                
                results[case_num] = {
                    'covered_population': int(covered_population),
                    'covered_population_percent': (covered_population / total_population * 100),
                    'covered_zones': len(covered_zones),
                    'covered_area': len(covered_zones) * 0.01,  # Assuming each zone is 0.01 km²
                    'covered_area_percent': (len(covered_zones) / len(self.zones) * 100),
                    'iterations': len(selected_locations),
                    'cpu_time': cpu_time
                }
                
                # Add case-specific metrics
                if case_num == 2:
                    accessibility = sum(self.bus_accessibility[i] for i in covered_zones)
                    max_accessibility = sum(self.bus_accessibility.values())
                    results[case_num]['accessibility'] = accessibility
                    results[case_num]['accessibility_percent'] = (accessibility / max_accessibility * 100)
                elif case_num == 3:
                    accessibility = sum(self.metro_accessibility[i] for i in covered_zones)
                    max_accessibility = sum(self.metro_accessibility.values())
                    results[case_num]['accessibility'] = accessibility
                    results[case_num]['accessibility_percent'] = (accessibility / max_accessibility * 100)
                elif case_num == 4:
                    poi_count = sum(self.poi_count[i] for i in covered_zones)
                    total_pois = sum(self.poi_count.values())
                    results[case_num]['poi_count'] = poi_count
                    results[case_num]['poi_percent'] = (poi_count / total_pois * 100)

        return results

    def format_results_table(self, results, case_number):
        """Format results into a table similar to the example images."""
        if case_number not in results:
            return "No results available for this case."

        headers = [
            "s", "Dc", 
            "Covered\npopulation", "Covered\npopulation",
            "Covered land zones", "Covered land zones", "Covered land zones",
            "nz", "CPU time"
        ]
        headers_second_row = [
            "No.", "[m]",
            "No.", "[%]",
            "No.", "[km²]", "[%]",
            "No.", "[s]"
        ]

        if case_number in [2, 3]:
            headers.extend(["Accessibility measure", "Accessibility measure"])
            headers_second_row.extend(["-", "[%]"])
        elif case_number == 4:
            headers.extend(["POIs", "POIs"])
            headers_second_row.extend(["No.", "[%]"])

        data = [[
            self.NUM_LOCATIONS,
            int(self.DISTANCE_THRESHOLD * 1000),  # Convert back to meters
            results[case_number]['covered_population'],
            f"{results[case_number]['covered_population_percent']:.2f}",
            results[case_number]['covered_zones'],
            f"{results[case_number]['covered_area']:.2f}",
            f"{results[case_number]['covered_area_percent']:.2f}",
            results[case_number]['iterations'],
            f"{results[case_number]['cpu_time']:.2f}"
        ]]

        if case_number in [2, 3]:
            data[0].extend([
                f"{results[case_number]['accessibility']:.2f}",
                f"{results[case_number]['accessibility_percent']:.2f}"
            ])
        elif case_number == 4:
            data[0].extend([
                results[case_number]['poi_count'],
                f"{results[case_number]['poi_percent']:.2f}"
            ])

        return tabulate(data, headers=headers_second_row, tablefmt='grid', 
                       stralign='right', numalign='right')

def tableResult(path):
    """Execute the optimization for all test configurations."""
    try:
        test_configurations = [
            (5, 200), (5, 400),
            (7, 200), (7, 400),
            (10, 200), (10, 400),
            
        ]
        
        all_results = []
        
        for num_locations, distance in test_configurations:
            optimizer = EScooterLocationOptimizer(
                path, 
                distance_threshold=distance/1000,  # Convert to kilometers
                num_locations=num_locations
            )
            results = optimizer.optimize_locations()
            
            for case_num in range(1, 5):
                print(f"\nResults of Case {case_num} (obj. Function f{case_num}(y)):")
                print(optimizer.format_results_table(results, case_num))

    except FileNotFoundError:
        print(f"Error: JSON data file not found at {path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()