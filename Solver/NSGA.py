from Solver.Solution import *
import copy
import sys


def min_tasks_per_truck(solution):
    return max(solution.tasks_per_truck.values())


def min_total_time(solution):
    return solution.time_total


def min_idle_time(solution):
    return solution.time_idle


class NSGAII:
    def __init__(self, graph, task_array, trucks_array):
        self.objective_functions = [min_tasks_per_truck, min_total_time, min_idle_time]
        self.objective_min = [0, 0, 0]
        self.objective_max = [1000, 100000, 100000]
        self.solution_size = len(task_array)
        self.population_size = 20
        self.tournament_size = 3
        self.prob_cross = 0.7
        self.prob_mutation = 0.002 * self.solution_size

        self.parents = np.array([]).astype(Solution)
        self.offspring = np.array([]).astype(Solution)
        self.population = np.array([]).astype(Solution)
        self.population_eval = np.empty((self.population_size, len(self.objective_functions)))

        self.graph = graph
        self.tasks = task_array
        self.trucks = trucks_array

    def init_population(self):
        self.parents = np.array(
            [Solution(self.graph, self.tasks, self.trucks, idx=i) for i in range(self.population_size // 2)])
        self.population = self.parents
        self.eval_population()
        self.gen_offspring()
        self.gen_population()

    def crossover(self, solution1, solution2):
        cross_point1, cross_point2 = sorted([random.randint(0, self.solution_size - 1),
                                             random.randint(0, self.solution_size - 1)])
        solution_child1 = np.concatenate((solution1.solution[:cross_point1],
                                          solution2.solution[cross_point1:cross_point2],
                                          solution1.solution[cross_point2:]))
        solution_child2 = np.concatenate((solution2.solution[:cross_point1],
                                          solution1.solution[cross_point1:cross_point2],
                                          solution2.solution[cross_point2:]))

        return Solution(self.graph, self.tasks, self.trucks, solution_child1), \
               Solution(self.graph, self.tasks, self.trucks, solution_child2)

    def mutation(self, solution):
        point = random.randint(0, self.solution_size - 1)
        new_truck_id = self.trucks[random.randint(0, len(self.trucks) - 1)].id
        solution.solution[point] = [new_truck_id, solution.solution[point][1]]

    def tournament(self, solutions):
        chosen = np.array([]).astype(Solution)
        density = np.array([], dtype=int)
        for _ in range(self.tournament_size):
            ordered_idx = random.randint(0, len(solutions) - 1)
            solution = solutions[ordered_idx]
            chosen = np.concatenate((chosen, [solution]))
            density = np.concatenate((density, [ordered_idx]))
        frontier_idx = self.get_idx_non_dominated(chosen)
        return (chosen[frontier_idx])[np.argmin(density[frontier_idx])]

    def get_idx_non_dominated(self, solutions):
        idx_non_dominated = np.array([], dtype=int)
        for i in range(len(solutions)):
            dominated = False
            for j in range(len(solutions)):
                if i != j and (self.population_eval[solutions[j].idx] < self.population_eval[solutions[i].idx]).all():
                    dominated = True
                    break
            if not dominated:
                idx_non_dominated = np.concatenate((idx_non_dominated, [i]))
        return idx_non_dominated

    def get_idx_order_density(self, solutions):
        distances = {i.idx: 0 for i in solutions}
        for objective in range(len(self.objective_functions)):
            objective_order = np.argsort([self.population_eval[i.idx, objective] for i in solutions])
            tmp_solutions = solutions[objective_order]
            distances[tmp_solutions[0].idx] = distances[tmp_solutions[-1].idx] = np.inf
            for solution in range(1, len(tmp_solutions) - 1):
                distances[tmp_solutions[solution].idx] += \
                    (self.population_eval[tmp_solutions[solution + 1].idx, objective] -
                     self.population_eval[tmp_solutions[solution - 1].idx, objective]) / \
                    (self.objective_max[objective] - self.objective_min[objective])
        return np.argsort(-np.array(list(distances.values())))

    def gen_parents(self):
        self.parents = np.array([]).astype(Solution)
        tmp_population = self.population[:]
        room = self.population_size // 2
        while room > 0:
            frontier_idx = self.get_idx_non_dominated(tmp_population)
            density_order_idx = self.get_idx_order_density(tmp_population[frontier_idx])
            for i in density_order_idx:
                self.parents = np.concatenate((self.parents, [tmp_population[frontier_idx[i]]]))
                room -= 1
                if room <= 0:
                    break
            tmp_population = np.delete(tmp_population, frontier_idx, 0)

    def gen_offspring(self):
        self.offspring = np.array([]).astype(Solution)
        sorted_parents = self.parents[self.get_idx_order_density(self.parents)]
        for _ in range(self.population_size // 4):
            cross = random.random()
            parent1 = self.tournament(sorted_parents)
            parent2 = self.tournament(sorted_parents)
            if cross < self.prob_cross:
                child1, child2 = self.crossover(parent1, parent2)
                mut1 = random.random()
                mut2 = random.random()
                if mut1 < self.prob_mutation:
                    self.mutation(child1)
                if mut2 < self.prob_mutation:
                    self.mutation(child2)
                child1.fix_task_order()
                child2.fix_task_order()
                self.offspring = np.concatenate((self.offspring, [child1, child2]))
            else:
                self.offspring = np.concatenate((self.offspring, [copy.deepcopy(parent1), copy.deepcopy(parent2)]))

    def gen_population(self):
        self.population = np.concatenate((self.parents, self.offspring))
        self.eval_population()

    def eval_population(self):
        for solution_idx in range(len(self.population)):
            self.population[solution_idx].eval()
            self.population[solution_idx].idx = solution_idx
            for objective in range(len(self.objective_functions)):
                self.population_eval[solution_idx, objective] = self.objective_functions[objective](
                    self.population[solution_idx])

    def run(self, generations):
        self.init_population()
        for i in range(generations):
            self.gen_parents()
            self.gen_offspring()
            self.gen_population()

    def run_debug(self, generations):
        orig_stdout = sys.stdout
        output_file = open('NSGA_debug.txt', 'w')
        sys.stdout = output_file
        np.set_printoptions(suppress=True)

        self.init_population()
        print('Initial Population:')
        print(self.population)
        print('-' * 100)
        for i in range(generations):
            print('ITERATION %d:' % i)
            print('Population:')
            print(self.population)
            print('+' * 50)
            print('Fitness:')
            print(self.population_eval)
            print('+' * 50)

            self.gen_parents()
            print('Parents:')
            print(self.parents)
            print('+' * 50)

            self.gen_offspring()
            print('Offspring:')
            print(self.offspring)
            print('+' * 50)

            self.gen_population()
            print('New Population:')
            print(self.population)
            print('-' * 100)

        print('Final Population (%d generations):' % generations)
        print(self.population)
        print('Fitness:')
        print(self.population_eval)

        sys.stdout = orig_stdout
        output_file.close()
