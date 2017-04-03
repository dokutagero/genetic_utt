import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
import utils.load_data as load_data
from app.FitnessFunctionTT import FitnessFunctionTT as fftt
import csv


# def main():

# python2 memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000
runtime = sys.argv[-1]

data = load_data.load(sys.argv[1:])
fitness_model = fftt(data)
#
mutation_prob = 0.05
pop_size = 20
ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob,
                            fitness_model=fitness_model)
ga.genetic_simulation()



# offspring = ga.recombination(ga.population[0], ga.population[1])



    # pass

#
# if __name__ == "__main__":
#     main()
