# import GeneticAlgorithmBase
import numpy as np
import time
from collections import Counter
import FitnessFunctionTT as fftt
import random
from Timetable import Timetable
import pdb
import copy

class GeneticAlgorithmPureTT():

    def __init__(self, data, population_size, mutation_prob, fitness_model):
        self.population_size = population_size
        self.mutation_prob = mutation_prob
        self.data = data
        self.fitness_model = fitness_model

        self.population = []
        self.initialize_population()

        self.best_individual = None
        self.print_population(self.population[0].schedule)


    def genetic_simulation(self):
        init_time = time.time()
        iteration = 0

        score_list = [individual.score for individual in self.population]
        best_individual = score_list.index(min(score_list))
        self.best_individual = self.population[best_individual]
        print "Best score after initialization: ", self.best_individual.score

        while ((time.time() - init_time) < self.data["run_time"]):
            # Select 4 individuals randomly and return best of pairs
            p1, p2 = self.selection()
            o1, o2 = self.recombination(self.population[p1], self.population[p2])
            o1_prime, o2_prime = self.mutation((o1, o2))
            # Select 4 individuals and return worst of pairs
            w1, w2 = self.selection(best_selection=False)
            self.population[w1] = o1_prime
            self.population[w2] = o2_prime

            iteration += 1

        score_list = [individual.score for individual in self.population]
        best_individual = score_list.index(min(score_list))

        self.best_individual = self.population[best_individual]
        self.print_population(self.best_individual.schedule)

        print "Best score: ", self.best_individual.score
        # print 'The score should be: ', self.best_individual.calc_score_total(save=False)
        print 'Iterations: ', iteration


    def initialize_population(self):
        for i in xrange(self.population_size):
            Individual = Timetable(self.data)
            self.population.append(Individual)


    def evaluation(self, Individual):
        return self.fitness_model.evaluate(Individual)


    def selection(self, best_selection=True):
        individual_indices = np.random.choice(range(len(self.population)), size=4, replace=False)
        # pdb.set_trace()
        fitness_values = [self.population[ind].score for ind in individual_indices]
        # fitness_values = [self.evaluation(self.population[individual]) for individual in individual_indices]

        if best_selection:
            return (individual_indices[fitness_values.index(min(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(min(fitness_values[2], fitness_values[3]))])
        else:
            return (individual_indices[fitness_values.index(max(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(max(fitness_values[2], fitness_values[3]))])


    def recombination(self, Parent1, Parent2):
        # We obtain the random 2D cuts for each parent.
        row_cut1, row_cut2 = np.random.choice(range(Parent1.schedule.shape[0]), size=2)
        col_cut1, col_cut2 = np.random.choice(range(Parent1.schedule.shape[1]), size=2)

        # Before performing the PMX crossover, the offspring is equal to the parents.
        offspring1 = copy.deepcopy(Parent1)
        offspring2 = copy.deepcopy(Parent2)

        offspring = [offspring1, offspring2]

        # offspring1 is copy of Parent2 and offspring2 is copy of Parent1
        # This is the reason of having them in opposite orders in the next for.
        for child, parent in zip(offspring, [Parent2, Parent1]):
            for r in range(row_cut1, row_cut2 + 1):
                for c in range(col_cut1, col_cut2 + 1):
                    parent_course2swap = parent.schedule[r,c]
                    child_course2swap = child.schedule[r,c]

                    if parent_course2swap != -1:
                        idcs_child_candidates = child.course_positions[parent_course2swap]
                        # If there are scheduled courses.
                        if idcs_child_candidates:
                            for position, idx_candidate in enumerate(idcs_child_candidates):
                                if(
                                child.check_single_conflict(idx_candidate, (r, c)) or
                                child.check_single_conflict((r, c), idx_candidate) or
                                child.check_single_availability((r,c), idx_candidate[1]) or
                                child.check_single_availability(idx_candidate, c) or
                                child.check_single_lecturer((r,c), idx_candidate) or
                                child.check_single_lecturer(idx_candidate, (r,c))
                                ):
                                    # If we can't swap it with the first candidate,
                                    # we check the next one.
                                    continue
                                else:
                                    child.swap_courses(idx_candidate, (r,c))


        return offspring


    def mutation(self, Offspring):
        for Child in Offspring:
            child = Child.schedule
            probability_matrix = np.random.rand(child.shape[0], child.shape[1])
            mutation_idcs = np.where(probability_matrix <= self.mutation_prob)
            for room, ts in zip(mutation_idcs[0], mutation_idcs[1]):
                row = np.random.randint(0, child.shape[0])
                col = np.random.randint(0, child.shape[1])
                if (
                    Child.check_single_conflict((room,ts), (row,col)) or
                    Child.check_single_conflict((row, col), (room, ts)) or
                    Child.check_single_availability((row,col), ts) or
                    Child.check_single_availability((room, ts), col) or
                    Child.check_single_lecturer((row,col), (room, ts)) or
                    Child.check_single_lecturer((room, ts), (row,col))
                ):
                    continue

                Child.swap_courses((room, ts), (row, col))

        return Offspring


    def replacement(self):
        pass


    def print_population(self, individual, filename='first_output.sol'):
        with open(filename, 'w'): pass
        for course in self.data["courses"].keys():
            course_room, course_tslots = np.where(individual == int(course[1:]))
            days = [day/self.data['basics']['periods_per_day'] for day in course_tslots]
            periods = [day%self.data['basics']['periods_per_day'] for day in course_tslots]


            with open(filename, 'a') as outputfile:
                for day, period, room in zip(days, periods, course_room):
                    print >> outputfile, course, day, period, 'R'+'%04d' % room
