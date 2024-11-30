from docplex.cp.model import CpoModel

# -------------------------------------------------------------------------
# Problem Data
# -------------------------------------------------------------------------

# Sets (example data)
Zones = range(3)  # Zones: {0, 1, 2}
Locations = range(4)  # Locations: {0, 1, 2, 3}

# Parameters
Population = [1000, 1500, 1200]
Distance = [
    [2.5, 1.3, 3.4, 0.4],
    [1.8, 2.2, 0.5, 1.6],
    [3.2, 1.9, 2.1, 0.3]
]
DistanceThreshold = 2.0
MaxLocations = 2

# Derived Parameters
DistanceCoverage = [[1 if Distance[i][j] <= DistanceThreshold else 0 for j in Locations] for i in Zones]

# -------------------------------------------------------------------------
# Model Definition
# -------------------------------------------------------------------------

# Create the constraint programming model
model = CpoModel(name="E-scooter Location Problem")

# Decision Variables
x = [model.binary_var(name=f"x_{j}") for j in Locations]  # 1 if location j is selected
y = [model.binary_var(name=f"y_{i}") for i in Zones]  # 1 if zone i is covered

# Objective: Maximize population coverage
model.add(
    model.maximize(
        model.sum(Population[i] * y[i] for i in Zones)
    )
)

# -------------------------------------------------------------------------
# Constraints
# -------------------------------------------------------------------------

# Coverage constraints: Zone `i` is covered if any selected location can cover it
for i in Zones:
    model.add(y[i] <= model.sum(DistanceCoverage[i][j] * x[j] for j in Locations))

# Maximum number of locations constraint
model.add(model.sum(x[j] for j in Locations) <= MaxLocations)

# -------------------------------------------------------------------------
# Solve the Model
# -------------------------------------------------------------------------

solution = model.solve()

# -------------------------------------------------------------------------
# Display Results
# -------------------------------------------------------------------------

if solution:
    print("Optimal solution found:")
    print(f"Selected locations (x): {[solution[x[j]] for j in Locations]}")
    print(f"Covered zones (y): {[solution[y[i]] for i in Zones]}")
    print(f"Total Population Covered: {solution.get_objective_values()[0]}")
else:
    print("No solution found!")
