# import GeneticAlgorithmBase
import numpy as np

class GeneticAlgorithmPureTT():

    def __init__(self, data, population_size, mutation_prob):
        self.population_size = population_size
        self.mutation_prob = mutation_prob
        self.data = data

        # Create random initial population
        self.population = self.initialization(data["basics"]["rooms"],
                        data["basics"]["periods_per_day"] * data["basics"]["days"])




    def initialization(self, num_rooms, timeslots):
        population = []

        for i in range(self.population_size):
            individual = np.zeros(shape=(num_rooms, timeslots), dtype=np.int8) - 1
            idcs = [idcs for idcs, val in np.ndenumerate(individual)]
            np.random.shuffle(idcs)

            for course, course_info in self.data["courses"].iteritems():
                for num_lecture in range(course_info["number_of_lectures"]):
                    ind = idcs.pop()
                    individual[ind] = int(course[1:])


            while test_feasibilty(individual) != True:
                pass

            population.append(individual)

        return population

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

    def test_feasibilty(individual):

        for course, constraint in data["unavailability"].iteritems():
            course_no = int(course[1:])

        pass
