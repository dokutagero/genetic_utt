


class GeneticAlgorithmBase(object):

    def __init__(self, population_size):

        self.population_size = population_size
        self.mutation_prob = mutation_prob


    def initialization(self):
        pass


    def evaluation(self, fitness_func):
        pass


    def selection(self):
        pass


    def recombination(self):
        pass


    def mutation(self):
        pass


    def replacement(self):
        pass
