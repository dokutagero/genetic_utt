from __future__ import division
import utils.load_data as load_data
import sys
import csv
import os.path
import os
import numpy as np
import fnmatch

directory = 'tuning_outputs/test/'

# python test_aggregate.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 0

params = sys.argv[1:]

datasets = range(1,14)
population_sizes =  [100, 50, 35, 15, 10]
mutation_probabilities = [0.02, 0.05, 0.08, 0.15, 0.2]
compactness_initializations = [False]
no_runs = 4
runs = range(no_runs)

folder_name_1 = 'ps_15__mp0.2_cw_3'
folder_name_2 = 'ps_100__mp0.08_cw_4'

folder_name_1_old = 'ps_15_ci_False_mp0.2_cw_3'
folder_name_2_old = 'ps_100_ci_False_mp0.08_cw_4'

old = [1,5,12,13]
model = 1

results = {}
for model in [1,2]:
    for dataset in datasets:

        if model == 1:
            folder_name = folder_name_1
            folder_name_old = folder_name_1_old

            # 3, 0 -> index 2
            index = 2

        else:
            folder_name = folder_name_2
            folder_name_old = folder_name_2_old

            # 4,1  -> index 3
            index = 3


        path_test = directory+'dataset_'+str(dataset)+'/'

        for run in runs:
            folders = []

            for file in os.listdir(path_test):
                if fnmatch.fnmatch(file, folder_name_old+'*'):
                    folder_name = file
                    if not folder_name in folders:
                        folders.append(folder_name)
                elif fnmatch.fnmatch(file, folder_name+'*'):
                    folder_name = file
                    if not folder_name in folders:
                        folders.append(folder_name)
                else:
                    pass

            if dataset in old:
                file_path = folders[index]
            else:
                file_path = folders[0]

            p = path_test + file_path
            print p

            values = []
            print p+'/run'+str(run)+'.csv'
            with open(p+'/run'+str(run)+'.csv', 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=' ')
                csv_reader.next()
                # print csv_reader
                for score in csv_reader:
                    values.append(score[0])

            if dataset in old:
                minimum = int(float(values[-1]))

                if model == 1:
                    mutation = 0.2
                else:
                    mutation = 0.08

            else:
                minimum = int(float(values[-2]))
                mutation = (float(values[-1]))

            iterations = len(values)

            if results.has_key(dataset):
                results[dataset]['minimum'].append(minimum)
                results[dataset]['iterations'].append(iterations)
                results[dataset]['mutation'].append(mutation)
            else:
                results[dataset] = {"minimum": [minimum], "iterations": [iterations], 'mutation': [mutation]}


# matrix = np.chararray((14,5),itemsize=40)
#
# for j,(col, rows) in enumerate(results.iteritems()):
#     # for key in row:
#     print rows
    # for i,(row, val) in enumerate(rows.iteritems()):
        # mini, mut, iterat = val
        # print row, val
        # pass
        # print row, val
        # for in row:

            # print mini,mut, iterat
        # if j == 0 and i == 0:
        #     matrix[i,j] = ''
        #
        # if j == 0:
        #     header_row = ' '+str(row)
        #     matrix[i+1,j] = header_row
        #
        # if i == 0:
        #     header_col = ' '+str(col)
        #     matrix[i,j+1] = header_col
        #
        # values = results[col][row]
        # print values
        # values_dataset = [values[x:x+no_runs] for x in range(0,len(values),no_runs)]


#         avg = []
#         std = []
#         for vd in values_dataset:
#             tmp = map(lambda v: (v - min(vd))*100/min(vd), vd)
#             avg.append(sum(tmp) / no_runs)
#             std.append(np.std(tmp))
#             # print vd, map(lambda v: (v - minimum)*100/minimum, vd) ,sum(map(lambda v: (v - minimum)*100/minimum, vd)) / float(no_runs)
#
#         print '\naverage',  sum(avg) / float(no_runs)
#         print avg
#         print '\nstd', sum(std) / float(no_runs)
#         print std
#         avg = sum(avg) / float(no_runs)
#         std = sum(std) / float(no_runs)
#
#         avgs[i+1,j+1] = str("{0:.1f}".format(avg))
#         stds[i+1,j+1] = str("{0:.1f}".format(std))
#         both[i+1,j+1] = str("{0:.1f}".format(avg))+'; '+str("{0:.1f}".format(std))
#
#
# with open('tuning-avgs.csv', 'wb') as f:
#     csv.writer(f).writerows(avgs)
#
# with open('tuning-stds.csv', 'wb') as f:
#     csv.writer(f).writerows(stds)
#
# with open('tuning-both.csv', 'wb') as f:
#     csv.writer(f).writerows(both)
