import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
from app.GeneticAlgorithmNonPure import GeneticAlgorithmNonPure
import utils.load_data as load_data
from app.FitnessFunctionTT import FitnessFunctionTT as fftt
import csv

import numpy as np
import sys

import cProfile
import re, pstats, StringIO


# def main():

# python2 memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000
# python memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000


# ================== Grid search ======================
# runtime = 600
# runtime = sys.argv[-1]
#
# no_datasets    = 13
# repetitions    = 10
# mutation_probs = np.linspace(0,  0.5, 10, endpoint=True)
# pop_sizes      = np.linspace(10, 100, 10, endpoint=True)
#
# for i in range(1, (no_datasets+1)):
#     data = load_data.load(sys.argv[1:], i)
#     fitness_model = fftt(data)
#
#     for repetition in range(0, repetitions):
#         for mutation_prob in mutation_probs:
#             for pop_size in pop_sizes:
#                 sys.stdout=open("Search/test_" + str(i) + "_" + str(repetition) + "_" + str(mutation_prob) + "_" + str(pop_size) +".dat","w")
#                 print "Data set\tMutation probability\tPopulation size"
#                 print "Test"+('%02d' % i)+'\t',mutation_prob,'\t',pop_size
#                 ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob,fitness_model=fitness_model)
#                 ga.genetic_simulation()
#             sys.stdout.close()

# =====================================================




# ================== Regular code ======================

runtime = sys.argv[-1]
enable_profiler = False

if enable_profiler:
    pr = cProfile.Profile()
    pr.enable()

data = load_data.load(sys.argv[1:],index=1)

mutation_prob = 0.1
pop_size = 20
# ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob)
print '\n\nNON PURE:'
ga = GeneticAlgorithmNonPure(data, pop_size, mutation_prob)
ga.genetic_simulation()

print "\n\nPURE"
ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob)
ga.genetic_simulation()

if enable_profiler:
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


# =====================================================


# offspring = ga.recombination(ga.population[0], ga.population[1])



    # pass

#
# if __name__ == "__main__":
#     main()
