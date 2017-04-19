import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
import utils.load_data as load_data
from app.FitnessFunctionTT import FitnessFunctionTT as fftt
import csv

import numpy as np
import sys

import cProfile
import re, pstats, StringIO

import os




# python memetic_algo.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 1000
# datasets = [12,13,1,5]
datasets = [2,3,4,6,7,8,9,10,11]
run_time = 1

models_to_test = [(15, 0.2, (3,1)), (100, 0.08, (4,-2))]
#

params = sys.argv[1:]
params[-1] = run_time
for dataset in datasets:
    for pop_size, mutation_prob, window in models_to_test:
        for run in range(4):
            # data = load_data.load(sys.argv[1:])
            # data[-1] = run_time
            data = load_data.load(params, index=dataset)

            # Based on max number of lectures we define the crossover window
            num_lectures = []
            for k,v in data['courses'].iteritems():
                num_lectures.append(v['number_of_lectures'])

            # The value corresponding to the max number of lectures for all subjects
            max_lectures = max(num_lectures)


            crossover_window_size = (window[0], max_lectures+window[1])


            ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob,
                                crossover_window_size)
            ga.genetic_simulation()

            folder_name = 'ps_'+str(pop_size)+'_'+'_mp'+str(mutation_prob)+'_cw_'+str(crossover_window_size[0])+'_'+str(crossover_window_size[1])

            if not os.path.exists('tuning_outputs/test/dataset_'+str(dataset)):
                os.makedirs('tuning_outputs//test/dataset_'+str(dataset))

            if not os.path.exists('tuning_outputs/test/dataset_'+str(dataset)+'/'+folder_name):
                os.makedirs('tuning_outputs/test/dataset_'+str(dataset)+'/'+folder_name)

            with open('tuning_outputs/test/dataset_'+str(dataset)+'/'+folder_name+'/run'+str(run)+'.csv', 'wb') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                for score in ga.scores_per_iteration:
                    csv_writer.writerow([score])
                csv_writer.writerow([ga.get_real_mutation_rate()])
                # csv_writer.writerows(ga.scores_per_iteration)

            ga.print_population(ga.best_individual.schedule, 'tuning_outputs/test/dataset_'+str(dataset)+'/'+folder_name+'/timetable_output_run'+str(run)+'.sol')

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
