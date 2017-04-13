# import GeneticAlgorithmBase
from GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
import numpy as np
import time
from collections import Counter
import FitnessFunctionTT as fftt
import random
from TimetableNonPure import TimetableNonPure
import pdb
import copy


class GeneticAlgorithmNonPure(GeneticAlgorithmPureTT):

    def __init__(self, data, population_size, mutation_prob):
        GeneticAlgorithmPureTT.__init__(self, data, population_size, mutation_prob)

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
            P1 = self.population[p1]
            P2 = self.population[p2]

            P1.optimize_timeslots(timeslots=3, iterations=0.25)
            P2.optimize_timeslots(timeslots=3, iterations=0.25)

            o1, o2 = self.recombination(P1, P2)
            o1_prime, o2_prime = self.mutation((o1, o2))

            # Select 4 individuals and return worst of pairs
            w1, w2 = self.selection(best_selection=False)
            self.population[w1] = o1_prime
            self.population[w2] = o2_prime

            iteration += 1

        score_list = [individual.score for individual in self.population]
        best_individual = score_list.index(min(score_list))

        self.best_individual = self.population[best_individual]
        # self.best_individual.insert_unscheduled()
        self.best_individual.optimize_timeslots(timeslots='all', iterations='all')
        self.print_population(self.best_individual.schedule)

        print "Best score: ", self.best_individual.score
        print 'Penalties: \n', self.best_individual.calc_score_total(save=False,print_out=True)
        print 'Iterations: ', iteration

    def get_new_individual(self):
        Individual = TimetableNonPure(self.data)
        Individual.optimize_timeslots(iterations='random', timeslots='all')
        self.population.append(Individual)

    def discard_individual(self, index=None):
        if index==None:
            index = self.get_worst_individual()

        self.population.pop(index)

    def get_worst_individual(self):
        worst = None
        worst_score = 0
        for i, Individual in enumerate(self.population):
            if Individual.score > worst_score:
                worst = i
                worst_score = Individual.score

        return worst

    def initialize_population(self):
        for i in xrange(self.population_size):
            Individual = TimetableNonPure(self.data)
            self.population.append(Individual)

    def evaluation(self, Individual):
        return GeneticAlgorithmPureTT.evaluation(self,Individual)


    def selection(self, best_selection=True):
        individual_indices = np.random.choice(range(len(self.population)), size=4, replace=False)
        fitness_values = [self.population[ind].score for ind in individual_indices]

        if best_selection:
            return (individual_indices[fitness_values.index(min(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(min(fitness_values[2], fitness_values[3]))])
        else:
            return (individual_indices[fitness_values.index(max(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(max(fitness_values[2], fitness_values[3]))])


    def recombination(self, Parent1, Parent2):
        return GeneticAlgorithmPureTT.recombination(self,Parent1, Parent2)


    def mutation(self, Offspring):
        return GeneticAlgorithmPureTT.mutation(self,Offspring)

    def replacement(self):
        pass


    def print_population(self, individual, filename='first_output.sol'):
        GeneticAlgorithmPureTT.print_population(self,individual, filename)
