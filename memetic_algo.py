import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
import utils.load_data as load_data
from app.FitnessFunctionTT import FitnessFunctionTT as fftt
import csv

import numpy as np
import sys
import random

import cProfile
import re, pstats, StringIO


# def main():

# python2 memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000
# python memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000

# ================== Grid search ======================
runtime = 360
# runtime = sys.argv[-1]

# no_datasets    = np.arange(13)
no_datasets    = random.sample(range(1,13), 5)
repetitions    = 20
# mutation_probs = np.linspace(0,  0.5, 10, endpoint=True)
mutation_probs = [0.01, 0.02, 0.05, 0.1, 0.15, 0.2]
# pop_sizes      = np.linspace(10, 100, 10, endpoint=True)
pop_sizes      = [10,20,40,60,80,100]


for i in no_datasets:
    data = load_data.load(sys.argv[1:], i)
    fitness_model = fftt(data)

    for repetition in range(0, repetitions):
        for mutation_prob in mutation_probs:

            for pop_size in pop_sizes:
                sys.stdout=open("Data/grid-search_" + str(i) + "_" + str(repetition) + "_" + "%.2f" % (mutation_prob) + "_" + str(pop_size) +".dat","w")
                print "Data set\tMutation probability\tPopulation size"
                print "Test"+('%02d' % i)+'\t',mutation_prob,'\t',pop_size
                ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob,fitness_model=fitness_model)
                ga.genetic_simulation()
            # sys.stdout.close()

# =====================================================




# ================== Regular code ======================

# runtime = sys.argv[-1]
# enable_profiler = True
#
# if enable_profiler:
#     pr = cProfile.Profile()
#     pr.enable()
#
# data = load_data.load(sys.argv[1:])
# fitness_model = fftt(data)
# #
# mutation_prob = 0.02
# pop_size = 1
# ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob,
#                             fitness_model=fitness_model)
#
# ga.genetic_simulation()
#
#
# if enable_profiler:
#     pr.disable()
#     s = StringIO.StringIO()
#     sortby = 'cumulative'
#     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#     ps.print_stats()
#     print s.getvalue()


# =====================================================


#
# if __name__ == "__main__":
#     main()
