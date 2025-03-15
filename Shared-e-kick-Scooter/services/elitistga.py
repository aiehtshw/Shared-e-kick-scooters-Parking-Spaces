import random
import math
import json


class ElitistGAOptimizer:
    def __init__(self, data_file, distance_threshold=0.2, num_locations=5, pop_size=10, generations=5, mutation_rate=0.1):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.zones = json.load(f)

        self.DISTANCE_THRESHOLD = distance_threshold
        self.NUM_LOCATIONS = num_locations
        self.POP_SIZE = pop_size
        self.GENERATIONS = generations
        self.MUTATION_RATE = mutation_rate

        self.preprocess_data()

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of Earth in kilometers
        return c * r

    def preprocess_data(self):
        self.I = list(range(len(self.zones)))
        self.population = {i: zone.get('population', 0) for i, zone in enumerate(self.zones)}
        self.poi_count = {i: zone.get('poi_number', 0) for i, zone in enumerate(self.zones)}
        print("Preprocessing data...")
        self.coverage_matrix = self.compute_coverage_matrix()
        print("Coverage matrix computed.")

    def compute_coverage_matrix(self):
        coverage = {}
        for i in self.I:
            for j in self.I:
                dist = self.haversine_distance(
                    self.zones[i]['latitude'], self.zones[i]['longitude'],
                    self.zones[j]['latitude'], self.zones[j]['longitude']
                )
                coverage[(i, j)] = 1 if dist <= self.DISTANCE_THRESHOLD else 0
        return coverage

    def fitness(self, solution):
        selected_zones = [i for i, selected in enumerate(solution) if selected]
        population_coverage = sum(self.population[i] for i in selected_zones)
        poi_coverage = sum(self.poi_count[i] for i in selected_zones)
        return population_coverage, poi_coverage

    def initialize_population(self):
        print("\nInitializing population...")
        population = []
        for idx in range(self.POP_SIZE):
            solution = [0] * len(self.I)
            selected_indices = random.sample(self.I, self.NUM_LOCATIONS)
            for index in selected_indices:
                solution[index] = 1
            population.append(solution)
            print(f"Initial Solution {idx + 1}: {solution}")
        return population

    def select_parents(self, population, fitness_values):
        print("\nSelecting parents...")
        sorted_population = [x for _, x in sorted(zip(fitness_values, population), reverse=True)]
        elite = sorted_population[:self.POP_SIZE // 10]
        print("Elite solutions:")
        for idx, sol in enumerate(elite):
            print(f"Elite {idx + 1}: {sol}")
        return elite + random.choices(population, k=self.POP_SIZE - len(elite))

    def crossover(self, parent1, parent2):
        print("\nPerforming crossover...")
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        print(f"Parent 1: {parent1}")
        print(f"Parent 2: {parent2}")
        print(f"Child 1: {child1}")
        print(f"Child 2: {child2}")
        return child1, child2

    def mutate(self, solution):
        print("\nPerforming mutation...")
        for i in range(len(solution)):
            if random.random() < self.MUTATION_RATE:
                solution[i] = 1 - solution[i]
        print(f"Mutated solution: {solution}")
        return solution

    def optimize(self):
        print("Starting optimization...\n")
        population = self.initialize_population()
        best_solution = None
        best_fitness = (-float('inf'), -float('inf'))

        for gen in range(self.GENERATIONS):
            print(f"\n--- Generation {gen + 1} ---")
            fitness_values = [self.fitness(ind) for ind in population]
            print(f"Fitness values: {fitness_values}")

            for idx, (ind, fit) in enumerate(zip(population, fitness_values)):
                print(f"Solution {idx + 1}: {ind}, Fitness: {fit}")

            selected_parents = self.select_parents(population, fitness_values)

            next_population = []
            for i in range(0, len(selected_parents) - 1, 2):
                child1, child2 = self.crossover(selected_parents[i], selected_parents[i + 1])
                next_population.extend([child1, child2])

            next_population = [self.mutate(ind) for ind in next_population]
            population = next_population

            for ind, fit in zip(population, fitness_values):
                if fit > best_fitness:
                    best_fitness = fit
                    best_solution = ind

            print(f"Best solution so far: {best_solution}, Fitness: {best_fitness}")

        print("\nOptimization complete.")
        return best_solution, best_fitness


# Main execution
def execEga(path):

    optimizer = ElitistGAOptimizer(path)
    best_solution, best_fitness = optimizer.optimize()

    print("\nBest Solution Found:")
    print(f"Fitness: {best_fitness}")
    print(f"Solution: {best_solution}")
