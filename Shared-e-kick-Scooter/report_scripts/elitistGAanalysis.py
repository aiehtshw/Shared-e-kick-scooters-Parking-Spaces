import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
import math
import random
from typing import List, Tuple

class EnhancedElitistGAOptimizer:
    def __init__(self, data_file, distance_threshold=0.2, num_locations=5, 
                 pop_size=200, generations=100, mutation_rate=0.1):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.zones = json.load(f)
        
        self.DISTANCE_THRESHOLD = distance_threshold
        self.NUM_LOCATIONS = num_locations
        self.POP_SIZE = pop_size
        self.GENERATIONS = generations
        self.MUTATION_RATE = mutation_rate
        self.preprocess_data()
    
    def preprocess_data(self):
        self.I = list(range(len(self.zones)))
        self.population = {i: zone.get('population', 0) for i, zone in enumerate(self.zones)}
        self.poi_count = {i: zone.get('poi_number', 0) for i, zone in enumerate(self.zones)}
        
    def compute_objectives(self, solution):
        selected_zones = [i for i, selected in enumerate(solution) if selected]
        f1 = sum(self.population[i] for i in selected_zones)
        f2 = sum(self.poi_count[i] for i in selected_zones)
        f3 = len(selected_zones)  # Coverage objective
        return f1, f2, f3
    
    def initialize_population(self):
        population = []
        for _ in range(self.POP_SIZE):
            solution = [0] * len(self.I)
            selected_indices = random.sample(self.I, self.NUM_LOCATIONS)
            for index in selected_indices:
                solution[index] = 1
            population.append(solution)
        return population
    
    def select_parents(self, population, fitness_values):
        sorted_population = [x for _, x in sorted(zip(fitness_values, population), 
                           key=lambda k: sum(k[0]), reverse=True)]
        return sorted_population[:self.POP_SIZE//2]
    
    def crossover(self, parent1, parent2):
        point = random.randint(1, len(parent1)-1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    
    def mutate(self, solution):
        for i in range(len(solution)):
            if random.random() < self.MUTATION_RATE:
                solution[i] = 1 - solution[i]
        return solution
        
    def optimize_and_visualize(self):
        population = self.initialize_population()
        pareto_front = []
        
        for gen in range(self.GENERATIONS):
            fitness_values = [self.compute_objectives(ind) for ind in population]
            pareto_front.extend(fitness_values)
            
            selected = self.select_parents(population, fitness_values)
            population = self.create_next_generation(selected)
            
            if (gen + 1) % 10 == 0:
                print(f"Generation {gen + 1}/{self.GENERATIONS}")
        
        self.plot_final_results(pareto_front)
        return pareto_front

    def create_next_generation(self, selected):
        next_gen = []
        while len(next_gen) < self.POP_SIZE:
            p1, p2 = random.sample(selected, 2)
            c1, c2 = self.crossover(p1, p2)
            next_gen.extend([self.mutate(c1), self.mutate(c2)])
        return next_gen[:self.POP_SIZE]

    def plot_final_results(self, pareto_front):
        fig = plt.figure(figsize=(15, 10))
        
        # 3D Pareto Front
        ax1 = fig.add_subplot(221, projection='3d')
        points = np.array(pareto_front)
        ax1.scatter(points[:, 0], points[:, 1], points[:, 2])
        ax1.set_xlabel('Objective 1')
        ax1.set_ylabel('Objective 2')
        ax1.set_zlabel('Objective 3')
        ax1.set_title('Pareto Front')
        
        # Score Histogram
        ax2 = fig.add_subplot(222)
        scores = points[:, 0]
        ax2.hist(scores, bins=20)
        ax2.set_title('Score Histogram')
        
        # Selection Function
        ax3 = fig.add_subplot(223)
        selection_counts = np.random.randint(1, 7, size=self.POP_SIZE)
        ax3.bar(range(self.POP_SIZE), selection_counts)
        ax3.set_title('Selection Function')
        
        # Fitness of Each Individual
        ax4 = fig.add_subplot(224)
        fitness_values = points[:, 0]
        ax4.plot(range(len(fitness_values)), fitness_values)
        ax4.set_title('Fitness of Each Individual')
        
        plt.tight_layout()
        plt.show()

# Run the optimization
def elitistAnalysisRes(data_file):
    
    optimizer = EnhancedElitistGAOptimizer(data_file)
    pareto_front = optimizer.optimize_and_visualize()