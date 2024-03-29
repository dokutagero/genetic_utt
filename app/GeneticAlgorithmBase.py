from abc import ABCMeta, abstractmethod
import numpy


class GeneticAlgorithmBase(object):

    __metaclass__ = ABCMeta

    def __init__(self, population_size, mutation_prob):

        self.population_size = population_size
        self.mutation_prob = mutation_prob


    @abstractmethod
    def initialization(self):
        pass

    @abstractmethod
    def evaluation(self, fitness_func):
        pass

    @abstractmethod
    def selection(self):
        pass

    @abstractmethod
    def recombination(self):
        pass

    @abstractmethod
    def mutation(self):
        pass

    @abstractmethod
    def replacement(self):
        pass
