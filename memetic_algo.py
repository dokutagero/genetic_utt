import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
import utils.load_data as load_data
from app.FitnessFunctionTT import FitnessFunctionTT as fftt
import csv

import numpy as np
import sys

import cProfile
import re, pstats, StringIO
import matplotlib.pyplot as plt

import pickle
import os


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


population_sizes = [100]#, 50, 35, 15, 10]
mutation_probabilities = [0.02]#, 0.05, 0.08, 0.15, 0.2]
compactness_initializations = [False]#, True]
runs = range(5)
datasets = [1,2]
run_time = 1
#
# mutation_prob = 0.03
# pop_size = 20
for dataset in datasets:
    print sys.argv[1:]
    params = sys.argv[1:]
    params[-1] = run_time
    # data = load_data.load(sys.argv[1:])
    # data[-1] = run_time
    data = load_data.load(params, index=dataset)

    # Based on max number of lectures we define the crossover window
    num_lectures = []
    for k,v in data['courses'].iteritems():
        num_lectures.append(v['number_of_lectures'])

    # The value corresponding to the max number of lectures for all subjects
    max_lectures = max(num_lectures)
    print num_lectures
    print max_lectures
    horizontal_sizes = [3,4]

    crossover_window_sizes = [(hs,max_lectures-vs) for hs,vs in zip(4*[horizontal_sizes[0]]+4*[horizontal_sizes[1]], 2*[-2,-1,0,1])]
    print crossover_window_sizes

    for crossover_window_size in crossover_window_sizes:
        for mutation_prob in mutation_probabilities:
            for pop_size in population_sizes:
                for compactness_initialization in compactness_initializations:
                    for run in runs:

                        ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob,
                                            crossover_window_size, compactness_initialization)
                        ga.genetic_simulation()

                        folder_name = 'ps_'+str(pop_size)+'_'+'ci_'+str(compactness_initialization)+'_mp'+str(mutation_prob)+'_cw_'+str(crossover_window_size[0])+'_'+str(crossover_window_size[1])
                        # check if folder for this experiments exists.
                        # If not, create one
                        if not os.path.exists('tuning_outputs/dataset_'+str(dataset)):
                            os.makedirs('tuning_outputs/dataset_'+str(dataset))

                        if not os.path.exists('tuning_outputs/dataset_'+str(dataset)+'/'+folder_name):
                            os.makedirs('tuning_outputs/dataset_'+str(dataset)+'/'+folder_name)

                        with open('tuning_outputs/dataset_'+str(dataset)+'/'+folder_name+'/run'+str(run)+'.pkl', 'wb') as picklefile:
                            pickle.dump(ga, picklefile)

                        ga.print_population(ga.best_individual.schedule, 'tuning_outputs/dataset_'+str(dataset)+'/'+folder_name+'/timetable_output_run'+str(run)+'.sol')

                        print '*'*20
                        print folder_name
                        print 'run: ', run
                        print '*'*20







# plt.plot(ga.scores_per_iteration)
# plt.show()

#
# if enable_profiler:
#     pr.disable()
#     s = StringIO.StringIO()
#     sortby = 'cumulative'
#     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#     ps.print_stats()
#     print s.getvalue()


# =====================================================


# offspring = ga.recombination(ga.population[0], ga.population[1])



    # pass

#
# if __name__ == "__main__":
#     main()
