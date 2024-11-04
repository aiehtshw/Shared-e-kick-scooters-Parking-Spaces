import numpy as np
import pandas as pd
from deap import base, creator, tools, algorithms
import random
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import seaborn as sns

class MCPLModel:
    def __init__(self, 
                 zones: List[int],
                 candidate_locations: List[int],
                 bus_stops: List[int],
                 train_stations: List[int],
                 population_data: Dict[int, float],
                 distance_matrix: np.ndarray,
                 time_to_bus: np.ndarray,
                 time_to_train: np.ndarray,
                 poi_data: Dict[int, int],
                 max_locations: int,
                 distance_threshold: float,
                 time_threshold: float):
        
        self.zones = zones
        self.candidate_locations = candidate_locations
        self.bus_stops = bus_stops
        self.train_stations = train_stations
        self.population_data = population_data
        self.distance_matrix = distance_matrix
        self.time_to_bus = time_to_bus
        self.time_to_train = time_to_train
        self.poi_data = poi_data
        self.max_locations = max_locations
        self.distance_threshold = distance_threshold
        self.time_threshold = time_threshold
        
        # Calculate coverage matrices
        self.distance_coverage = (distance_matrix <= distance_threshold).astype(int)
        
        # Create bus and train coverage matrices with correct dimensions
        self.bus_coverage = np.zeros((len(zones), len(candidate_locations)))
        self.train_coverage = np.zeros((len(zones), len(candidate_locations)))
        
        # Fill coverage matrices based on time thresholds
        for i in range(len(zones)):
            for j in range(len(candidate_locations)):
                # Bus coverage
                if np.any(time_to_bus[i, :] <= time_threshold):
                    self.bus_coverage[i, j] = 1
                    
                # Train coverage
                if np.any(time_to_train[i, :] <= time_threshold):
                    self.train_coverage[i, j] = 1
        
    def calculate_population_coverage(self, solution: List[int]) -> float:
        """Calculate population coverage objective (f1)"""
        covered_zones = np.any(self.distance_coverage[:, solution], axis=1)
        return sum(self.population_data[zone] for zone, is_covered 
                  in zip(self.zones, covered_zones) if is_covered)
    
    def calculate_transit_coverage(self, solution: List[int]) -> Tuple[float, float]:
        """Calculate transit coverage objectives (f2a and f2b)"""
        bus_access = np.sum(np.any(self.bus_coverage[:, solution], axis=1))
        train_access = np.sum(np.any(self.train_coverage[:, solution], axis=1))
        return bus_access, train_access
    
    def calculate_poi_coverage(self, solution: List[int]) -> float:
        """Calculate POI coverage objective (f3)"""
        covered_zones = np.any(self.distance_coverage[:, solution], axis=1)
        return sum(self.poi_data[zone] for zone, is_covered 
                  in zip(self.zones, covered_zones) if is_covered)
    
    def evaluate_solution(self, solution: List[int]) -> Tuple[float, float, float, float]:
        """Evaluate all objectives for a given solution"""
        if len(solution) > self.max_locations:
            return 0, 0, 0, 0
        
        pop_coverage = self.calculate_population_coverage(solution)
        bus_coverage, train_coverage = self.calculate_transit_coverage(solution)
        poi_coverage = self.calculate_poi_coverage(solution)
        
        return pop_coverage, bus_coverage, train_coverage, poi_coverage

class GeneticAlgorithm:
    def __init__(self, 
                 mcpl_model: MCPLModel,
                 population_size: int = 100,
                 generations: int = 50 ,
                 crossover_prob: float = 0.7,
                 mutation_prob: float = 0.2):
        
        self.mcpl = mcpl_model
        self.population_size = population_size
        self.generations = generations
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        
        # Reset DEAP creators if they already exist
        if 'FitnessMulti' in creator.__dict__:
            del creator.FitnessMulti
        if 'Individual' in creator.__dict__:
            del creator.Individual
            
        # Setup DEAP
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0, 1.0))
        creator.create("Individual", list, fitness=creator.FitnessMulti)
        
        self.toolbox = base.Toolbox()
        self.setup_toolbox()
        
    def setup_toolbox(self):
        """Setup genetic operators"""
        # Individual creation
        self.toolbox.register("indices", random.sample, 
                            range(len(self.mcpl.candidate_locations)), 
                            self.mcpl.max_locations)
        self.toolbox.register("individual", tools.initIterate, 
                            creator.Individual, self.toolbox.indices)
        self.toolbox.register("population", tools.initRepeat, 
                            list, self.toolbox.individual)
        
        # Genetic operators
        self.toolbox.register("evaluate", self.mcpl.evaluate_solution)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
        self.toolbox.register("select", tools.selNSGA2)
    
    def run(self) -> Tuple[List[List[int]], List[Tuple[float, float, float, float]]]:
        """Run the genetic algorithm"""
        pop = self.toolbox.population(n=self.population_size)
        
        # Statistics setup
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)
        
        # Run algorithm
        final_pop, logbook = algorithms.eaMuPlusLambda(
            pop, self.toolbox,
            mu=self.population_size, 
            lambda_=self.population_size,
            cxpb=self.crossover_prob,
            mutpb=self.mutation_prob,
            ngen=self.generations,
            stats=stats,
            verbose=True
        )
        
        # Get Pareto front
        pareto_front = tools.sortNondominated(final_pop, len(final_pop))[0]
        
        return (
            [list(ind) for ind in pareto_front],
            [ind.fitness.values for ind in pareto_front]
        )

def main():
    # Example data with consistent dimensions
    n_zones = 10
    n_candidates = 20
    n_bus_stops = 5
    n_train_stations = 3
    
    zones = list(range(n_zones))
    candidate_locations = list(range(n_candidates))
    bus_stops = list(range(n_bus_stops))
    train_stations = list(range(n_train_stations))
    
    # Sample data with consistent dimensions
    population_data = {i: random.randint(1000, 5000) for i in zones}
    distance_matrix = np.random.rand(n_zones, n_candidates)
    time_to_bus = np.random.rand(n_zones, n_bus_stops)
    time_to_train = np.random.rand(n_zones, n_train_stations)
    poi_data = {i: random.randint(1, 10) for i in zones}
    
    # Create MCPL model
    mcpl = MCPLModel(
        zones=zones,
        candidate_locations=candidate_locations,
        bus_stops=bus_stops,
        train_stations=train_stations,
        population_data=population_data,
        distance_matrix=distance_matrix,
        time_to_bus=time_to_bus,
        time_to_train=time_to_train,
        poi_data=poi_data,
        max_locations=5,
        distance_threshold=0.5,
        time_threshold=0.3
    )
    
    # Create and run GA
    ga = GeneticAlgorithm(
        mcpl,
        population_size=50,  # Reduced for faster execution
        generations=30       # Reduced for faster execution
    )
    solutions, fitness_values = ga.run()
    
    # Visualize results
    visualize_results(solutions, fitness_values, 'pareto_front.png')
    
    # Print best solutions
    print("\nTop 5 solutions:")
    for i, (solution, fitness) in enumerate(zip(solutions[:5], fitness_values[:5])):
        print(f"\nSolution {i+1}:")
        print(f"Locations: {solution}")
        print(f"Population Coverage: {fitness[0]:.2f}")
        print(f"Bus Access: {fitness[1]:.2f}")
        print(f"Train Access: {fitness[2]:.2f}")
        print(f"POI Coverage: {fitness[3]:.2f}")

if __name__ == "__main__":
    main()