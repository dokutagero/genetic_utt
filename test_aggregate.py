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

folder_name_1 = 'ps_15__mp0.02_cw_3'
folder_name_2 = 'ps_35__mp0.02_cw_3'

folder_name_1_old = 'ps_15_ci_False_mp0.02_cw_3'
folder_name_2_old = 'ps_35_ci_False_mp0.02_cw_3'

old = [1,5,12,13]
model = 1

results = {}
for model in [1,2]:
    for dataset in datasets:

        if model == 1:
            folder_name = folder_name_1
            folder_name_old = folder_name_1_old

            # 3, -2 -> index 0
            index = 0

        else:
            folder_name = folder_name_2
            folder_name_old = folder_name_2_old

            # 3, 0  -> index 2
            index = 2


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

            values = []
            with open(p+'/run'+str(run)+'.csv', 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=' ')
                csv_reader.next()
                for score in csv_reader:
                    values.append(score[0])

            if dataset in old:
                minimum = int(float(values[-1]))

                if model == 1:
                    mutation = 0.02
                else:
                    mutation = 0.02

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


datasets_to_keep = [2,3,4,6,7,8,9,10,11]
i=0
name = ''
matrix = np.chararray((10,6),itemsize=40)
for j,(col, dset) in enumerate(results.iteritems()):

    if col == 11:
        print dset
    if col in datasets_to_keep:
        minimum = min(dset['minimum'])
        model1 = (dset['minimum'][:4], dset['mutation'][:4], dset['iterations'][:4])
        model2 = (dset['minimum'][4:], dset['mutation'][4:], dset['iterations'][4:])

        E_model1 = ( str("{0:.2f}".format(sum(model1[0]) / float(no_runs))) ,  str("{0:.2f}".format(sum((np.array(model1[0])-minimum)/minimum*100) / no_runs)),  str("{0:.2f}".format( np.std((np.array(model1[0])-minimum)/minimum*100)) ) ,  str("{0:.4f}".format(sum(model1[1]) / no_runs)), sum(model1[2]) / no_runs)
        E_model2 = ( str("{0:.2f}".format(sum(model2[0]) / float(no_runs))) ,  str("{0:.2f}".format(sum((np.array(model2[0])-minimum)/minimum*100) / no_runs)),  str("{0:.2f}".format( np.std((np.array(model2[0])-minimum)/minimum*100)) ) ,  str("{0:.4f}".format(sum(model2[1]) / no_runs)), sum(model2[2]) / no_runs)

        E_model = E_model2
        name = 'testing_'+folder_name_2_old+'.csv'

        matrix[0,0] = ''

        header_row = 'Dataset ' + str(col)
        matrix[i+1,0] = header_row

        if i == 0:
            header_col = ['Avg. score', 'Avg. gap', 'Avg. spreading', 'Real mutation rate', 'Avg. #iterations']
            matrix[i,1:6] = header_col


        matrix[i+1,1:6] = E_model
        i+=1

with open(name, 'wb') as f:
    csv.writer(f).writerows(matrix)
