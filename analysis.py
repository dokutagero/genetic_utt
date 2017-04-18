from __future__ import division
import utils.load_data as load_data
import sys
import csv
import os.path
import numpy as np

directory = 'tuning_outputs/'

# python analysis.py basic.utt courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 0

params = sys.argv[1:]

datasets = [1,5,12,13]
population_sizes =  [100, 50, 35, 15, 10]
mutation_probabilities = [0.02, 0.05, 0.08, 0.15, 0.2]
compactness_initializations = [False]
no_runs = 4
runs = range(no_runs)

results = {}
for dataset in datasets:
    path = directory+'dataset_'+str(dataset)

    data = load_data.load(params, index=dataset)

    num_lectures = []
    for k,v in data['courses'].iteritems():
        num_lectures.append(v['number_of_lectures'])
    max_lectures = max(num_lectures)

    horizontal_sizes = [3,4]
    crossover_window_sizes = [(hs,max_lectures+vs) for hs,vs in zip(4*[horizontal_sizes[0]]+4*[horizontal_sizes[1]], 2*[-2,-1,0,1])]

    for ps in population_sizes:
        for ci in compactness_initializations:
            for mp in mutation_probabilities:

                cw_i = -2
                for cw in crossover_window_sizes:
                    if cw[0] == 4 and cw_i == 2:
                        cw_i = -2
                    else:
                        cw_i+=1

                    folder_name = 'ps_'+str(ps)+'_'+'ci_'+str(ci)+'_mp'+str(mp)+'_cw_'+str(cw[0])+'_'+str(cw[1])
                    path_test = directory+'dataset_'+str(dataset)+'/'+folder_name

                    for run in runs:
                        file_path = path_test+'/run'+str(run)+'.csv'

                        if not os.path.isfile(file_path):
                            print "Missing ", file_path
                        else:
                            values = []
                            with open(file_path, 'rb') as csvfile:
                            	csv_reader = csv.reader(csvfile, delimiter=' ')
                            	csv_reader.next()
                            	for score in csv_reader:
                                    values.append(score[0])

                            minimum = int(float(values[-1]))
                            # print minimum
                            iterations = len(values)

                            key = str(ps)+' '+str(mp)
                            cw_key = str(cw[0])+' '+str(cw_i)
                            # print key
                            # print cw_i
                            # print cw_key
                            if results.has_key(cw_key):
                                if results[cw_key].has_key(key):
                                    results[cw_key][key].append(minimum)
                                else:
                                    results[cw_key][key] = [minimum]
                            else:
                                results[cw_key] = {key: [minimum]}


# table = {}
# for col, rows in results.iteritems():
#     for row in rows:
#         values = results[col][row]
#         minimum = min(values)
#         avg = sum(map(lambda v: (v - minimum)*100/minimum, values)) / len(values)
#         std = np.std(values)
#
#         if table.has_key(col):
#             table[col][row] = [avg, std]
#         else:
#             table[col] = {row: [avg, std]}


avgs = np.chararray((26,9),itemsize=40)
stds = np.chararray((26,9),itemsize=40)
both = np.chararray((26,9),itemsize=40)

for j,(col, rows) in enumerate(results.iteritems()):
    for i,row in enumerate(rows):
        # print i, row

        if j == 0 and i == 0:
            avgs[i,j] = ''
            stds[i,j] = ''
            both[i,j] = ''

        if j == 0:
            header_row = 'pop.size - mutation rate: '+str(row)
            avgs[i+1,j] = header_row
            stds[i+1,j] = header_row
            both[i+1,j] = header_row

        if i == 0:
            header_col = 'crossover-split: '+str(col)
            avgs[i,j+1] = header_col
            stds[i,j+1] = header_col
            both[i,j+1] = header_col


        values = results[col][row]
        values_dataset = [values[x:x+no_runs] for x in range(0,len(values),no_runs)]

        avg = []
        std = []
        for vd in values_dataset:
            tmp = map(lambda v: (v - min(vd))*100/min(vd), vd)
            avg.append(sum(tmp) / no_runs)
            std.append(np.std(tmp))
            # print vd, map(lambda v: (v - minimum)*100/minimum, vd) ,sum(map(lambda v: (v - minimum)*100/minimum, vd)) / float(no_runs)

        print '\naverage',  sum(avg) / float(no_runs)
        print avg
        print '\nstd', sum(std) / float(no_runs)
        print std
        avg = sum(avg) / float(no_runs)
        std = sum(std) / float(no_runs)

        avgs[i+1,j+1] = str("{0:.1f}".format(avg))
        stds[i+1,j+1] = str("{0:.1f}".format(std))
        both[i+1,j+1] = str("{0:.1f}".format(avg))+'; '+str("{0:.1f}".format(std))


with open('tuning-avgs.csv', 'wb') as f:
    csv.writer(f).writerows(avgs)

with open('tuning-stds.csv', 'wb') as f:
    csv.writer(f).writerows(stds)

with open('tuning-both.csv', 'wb') as f:
    csv.writer(f).writerows(both)
