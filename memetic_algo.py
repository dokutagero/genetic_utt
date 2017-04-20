import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
from app.MemeticAlgorithm import MemeticAlgorithm
import utils.load_data as load_data
import csv

import numpy as np
import sys

import cProfile
import re, pstats, StringIO
#import matplotlib.pyplot as plt

import os



# python2 memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000
# python memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000


# ================== Grid search ======================
'''
runtime = 600
runtime = sys.argv[-1]

no_datasets    = 13
repetitions    = 10
mutation_probs = np.linspace(0,  0.5, 10, endpoint=True)
pop_sizes      = np.linspace(10, 100, 10, endpoint=True)

for i in range(1, (no_datasets+1)):
    data = load_data.load(sys.argv[1:], i)
    fitness_model = fftt(data)

    for repetition in range(0, repetitions):
        for mutation_prob in mutation_probs:
            for pop_size in pop_sizes:
                sys.stdout=open("Search/test_" + str(i) + "_" + str(repetition) + "_" + str(mutation_prob) + "_" + str(pop_size) +".dat","w")
                print "Data set\tMutation probability\tPopulation size"
                print "Test"+('%02d' % i)+'\t',mutation_prob,'\t',pop_size
                ma = MemeticAlgorithm(data, pop_size, mutation_prob,fitness_model=fitness_model)
                ma.genetic_simulation()
            sys.stdout.close()
'''
# ===========================================================




# ============ Regular code (with profiling) ================
runtime = sys.argv[-1]
enable_profiler = False

pop_size = 20
mutation_prob = 0.015
dataset = 2

params = sys.argv[1:]
params[-1] = sys.argv[-1]

if enable_profiler:
    pr = cProfile.Profile()
    pr.enable()


data = load_data.load(params, index=dataset)

max_lectures = max([ course['number_of_lectures'] for course in data['courses'].values()])
horizontal_sizes = [3,4]
crossover_window_sizes = [(hs,max_lectures+vs) for hs,vs in zip(4*[horizontal_sizes[0]]+4*[horizontal_sizes[1]], 2*[-2,-1,0,1])]
crossover_window_size = crossover_window_sizes[0]

ma = MemeticAlgorithm(data, pop_size, mutation_prob,
                    crossover_window_size)
ma.genetic_simulation()


if enable_profiler:
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


# ================== Tuning code ======================
'''
population_sizes = [20,100, 50, 35, 15, 10]
mutation_probabilities = [0.02, 0.05, 0.08, 0.15, 0.2]
compactness_initializations = [False]
runs = range(4)
datasets = [12,13,1,5]

params = sys.argv[1:]
params[-1] = sys.argv[-1]

for dataset in datasets:
    data = load_data.load(params, index=dataset)

    max_lectures = max([ course['number_of_lectures'] for course in data['courses'].values()])
    horizontal_sizes = [3,4]

    crossover_window_sizes = [(hs,max_lectures+vs) for hs,vs in zip(4*[horizontal_sizes[0]]+4*[horizontal_sizes[1]], 2*[-2,-1,0,1])]

    for crossover_window_size in crossover_window_sizes:
        for mutation_prob in mutation_probabilities:
            for pop_size in population_sizes:
                for compactness_initialization in compactness_initializations:
                    for run in runs:

                        ma = MemeticAlgorithm(data, pop_size, mutation_prob,
                                            crossover_window_size, compactness_initialization)
                        ma.genetic_simulation()

                        folder_name = 'ps_'+str(pop_size)+'_'+'ci_'+str(compactness_initialization)+'_mp'+str(mutation_prob)+'_cw_'+str(crossover_window_size[0])+'_'+str(crossover_window_size[1])
                        # check if folder for this experiments exists.
                        # If not, create one
                        if not os.path.exists('tuning_outputs/dataset_'+str(dataset)):
                            os.makedirs('tuning_outputs/dataset_'+str(dataset))

                        if not os.path.exists('tuning_outputs/dataset_'+str(dataset)+'/'+folder_name):
                            os.makedirs('tuning_outputs/dataset_'+str(dataset)+'/'+folder_name)

                        with open('tuning_outputs/dataset_'+str(dataset)+'/'+folder_name+'/run'+str(run)+'.csv', 'wb') as csvfile:
                            csv_writer = csv.writer(csvfile, delimiter=',')
                            for score in ma.scores_per_iteration:
                                csv_writer.writerow([score])
                            # csv_writer.writerows(ma.scores_per_iteration)

                        ma.print_population(ma.best_individual.schedule, 'tuning_outputs/dataset_'+str(dataset)+'/'+folder_name+'/timetable_output_run'+str(run)+'.sol')

                        # print '*'*20
                        # print folder_name
                        # print 'run: ', run
                        # print '*'*20



# plt.plot(ma.scores_per_iteration)
# plt.show()
'''
# =====================================================
