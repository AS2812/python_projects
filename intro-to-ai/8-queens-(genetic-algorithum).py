import random

class Chromosome:
    def __init__(self, genes):
        self.genes = genes  # List representing queen positions on the chessboard
        self.fitness = self.calculate_fitness()

    def calculate_fitness(self):
        """
        Calculates the number of non-attacking pairs of queens
        (higher fitness indicates closer to solution)
        """
        fitness = 0
        for i in range(len(self.genes)):
            for j in range(i + 1, len(self.genes)):
                if self.genes[i] != self.genes[j] and abs(i - j) != abs(self.genes[i] - self.genes[j]):
                    fitness += 1
        return fitness

def create_initial_population(population_size):
    """
    Generates a population of chromosomes with random queen positions
    """
    population = []
    for _ in range(population_size):
        genes = [random.randint(0, 7) for _ in range(8)]  # 8 random integers for 8 queens
        population.append(Chromosome(genes))
    return population

def selection(population, tournament_size=2):
    """
    Tournament selection: Selects chromosomes with higher fitness for crossover
    """
    selected = []
    for _ in range(len(population)):
        competitors = random.sample(population, tournament_size)
        winner = max(competitors, key=lambda c: c.fitness)
        selected.append(winner)
    return selected

def crossover(parent1, parent2):
    """
    Single-point crossover: Exchanges genes between parents at a random crossover point
    """
    crossover_point = random.randint(1, 6)  # Avoid first and last queens for stability
    child1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
    child2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
    return Chromosome(child1_genes), Chromosome(child2_genes)

def mutation(chromosome, mutation_rate=0.01):
    """
    Randomly changes queen positions with a given mutation rate
    """
    for i in range(len(chromosome.genes)):
        if random.random() < mutation_rate:
            new_position = random.randint(0, 7)
            if new_position != chromosome.genes[i]:
                chromosome.genes[i] = new_position
    chromosome.fitness = chromosome.calculate_fitness()  # Recalculate fitness

def genetic_algorithm(population_size=100, generations=100, mutation_rate=0.01):
    """
    Main genetic algorithm loop for solving the 8-queens problem
    """
    population = create_initial_population(population_size)
    best_solution = None

    for generation in range(generations):
        # Selection
        selected = selection(population)

        # Crossover (ensure even number of children)
        children = []
        for i in range(0, len(selected), 2):
            child1, child2 = crossover(selected[i], selected[i + 1] if i + 1 < len(selected) else random.choice(population))
            children.append(child1)
            children.append(child2)

        # Mutation
        for child in children:
            mutation(child, mutation_rate)

        # Combine parents and children for next generation (handle population size)
        population = population[:population_size // 2] + children[:population_size // 2]

        # Find the best solution in current generation
        best_solution = max(population, key=lambda c: c.fitness)
        if best_solution.fitness == 28:  # All queens non-attacking
            break

    return best_solution

if __name__ == "__main__":
    solution = genetic_algorithm()
    print("Solution:", solution.genes)  # List of queen positions (0-7) representing columns
