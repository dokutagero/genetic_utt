# import GeneticAlgorithmBase
import numpy as np
import time
from collections import Counter
import FitnessFunctionTT as fftt
import random
from Timetable import Timetable
import pdb
import copy

class GeneticAlgorithmPureTT():

    def __init__(self, data, population_size, mutation_prob, fitness_model):
        self.population_size = population_size
        self.mutation_prob = mutation_prob
        self.data = data
        self.fitness_model = fitness_model

        self.population = []
        self.initialize_population()

        self.best_individual = None
        self.print_population(self.population[0].schedule)
        self.scores_per_iteration = []


    def genetic_simulation(self):
        init_time = time.time()
        iteration = 0
        random_offspring_counter = 0

        score_list = [individual.score for individual in self.population]
        best_individual = score_list.index(min(score_list))
        self.best_individual = self.population[best_individual]
        print "Best score after initialization: ", self.best_individual.score

        number_hc = 1

        while ((time.time() - init_time) < self.data["run_time"]):
            # Select 4 individuals randomly and return best of pairs
            p1, p2 = self.selection()
            self.population[p1].fill_unscheduled()
            self.population[p2].fill_unscheduled()
            if (time.time() - init_time) / float(self.data["run_time"]) > 0.75 and iteration%100==0:
                self.population[p1].room_hill_climb()
                self.population[p2].room_hill_climb()
                # number_hc -= 1


            # if iteration%300==0:
            #     self.population[p1].room_hill_climb()
            #     self.population[p2].room_hill_climb()
            if (len(np.where((self.population[p1].schedule - self.population[p2].schedule) == 0)[0]) / float(self.population[p1].schedule.size)) > 0.75:
                o1 = copy.deepcopy(self.population[p1])
                o2 = Timetable(self.data)
                random_offspring_counter += 1
                # print  'added random offspring: ', random_offspring_counter
            else:
                o1, o2 = self.recombination(self.population[p1], self.population[p2])
            # o1, o2 = self.population[p1], self.population[p2]
            o1_prime, o2_prime = self.mutation((o1, o2))
            # Select 4 individuals and return worst of pairs
            w1, w2 = self.selection(best_selection=False)
            self.population[w1] = o1_prime
            self.population[w2] = o2_prime

            iteration += 1

            score_list = [individual.score for individual in self.population]
            best_individual = score_list.index(min(score_list))
            self.scores_per_iteration.append(self.population[best_individual].score)

        score_list = [individual.score for individual in self.population]
        best_individual = score_list.index(min(score_list))

        self.best_individual = self.population[best_individual]
        self.print_population(self.best_individual.schedule)

        print "Best score: ", self.best_individual.score
        # print 'The score should be: ', self.best_individual.calc_score_total(save=False)
        print 'Iterations: ', iteration



    def initialize_population(self):
        for i in xrange(self.population_size):
            Individual = Timetable(self.data)
            self.population.append(Individual)


    def evaluation(self, Individual):
        return self.fitness_model.evaluate(Individual)


    def selection(self, best_selection=True, destruction=False):
        individual_indices = np.random.choice(range(len(self.population)), size=4, replace=False)
        # pdb.set_trace()
        fitness_values = [self.population[ind].score for ind in individual_indices]
        # fitness_values = [self.evaluation(self.population[individual]) for individual in individual_indices]

        if best_selection:
            worst1 = individual_indices[fitness_values.index(max(fitness_values[0], fitness_values[1]))]
            worst2 = individual_indices[fitness_values.index(max(fitness_values[2], fitness_values[3]))]

            if destruction and (len(np.where((self.population[worst1].schedule - self.population[worst2].schedule) == 0)[0]) / float(self.population[worst1].schedule.size)) > 0.75:
                self.population[worst1] = Timetable(self.data)
                self.population[worst2] = Timetable(self.data)

            return (individual_indices[fitness_values.index(min(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(min(fitness_values[2], fitness_values[3]))])
        else:
            return (individual_indices[fitness_values.index(max(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(max(fitness_values[2], fitness_values[3]))])


    def recombination(self, Parent1, Parent2):
        # We obtain the random 2D cuts for each parent.
        # row_cut1, row_cut2 = np.random.choice(range(Parent1.schedule.shape[0]), size=2)
        # col_cut1, col_cut2 = np.random.choice(range(Parent1.schedule.shape[1]), size=2)

        vertical_max_size = 3
        horizontal_max_size = 3

        # row_cut1 = np.random.choice(range(Parent1.schedule.shape[0]), size=1)
        # row_cut2 = min(np.random.choice(range(row_cut1, row_cut1 + vertical_max_size), size=1), Parent1.schedule.shape[0]-1)
        #
        # col_cut1 = np.random.choice(range(Parent1.schedule.shape[1]), size=1)
        # col_cut2 = min(np.random.choice(range(col_cut1, col_cut1 + horizontal_max_size), size=1), Parent1.schedule.shape[1]-1)

        row_cut1 = random.randint(0, Parent1.schedule.shape[0]-1)
        # Modify row_cut+1 if we want to avoid the option of selecting vectors instead of submatrices
        row_cut2 = min(random.randint(row_cut1, row_cut1 + vertical_max_size), Parent1.schedule.shape[0]-1)

        col_cut1 = random.randint(0, Parent1.schedule.shape[1]-1)
        col_cut2 = min(random.randint(col_cut1, col_cut1 + horizontal_max_size), Parent1.schedule.shape[1]-1)

        # Before performing the PMX crossover, the offspring is equal to the parents.
        offspring1 = copy.deepcopy(Parent1)
        offspring2 = copy.deepcopy(Parent2)

        offspring = [offspring1, offspring2]

        # offspring1 is copy of Parent2 and offspring2 is copy of Parent1
        # This is the reason of having them in opposite orders in the next for.
        for child, parent in zip(offspring, [Parent2, Parent1]):
            swap_counter = 0
            for r in range(row_cut1, row_cut2 + 1):
                for c in range(col_cut1, col_cut2 + 1):
                    parent_course2swap = parent.schedule[r,c]
                    child_course2swap = child.schedule[r,c]

                    if parent_course2swap == child_course2swap:
                        continue

                    scores = []
                    positions = []


                    # if parent_course2swap != -1:
                    idcs_child_candidates = child.course_positions[parent_course2swap]
                    # If there are scheduled courses.
                    candidates_outside_box = [candidate for candidate in idcs_child_candidates if candidate[0]<row_cut1 or
                                                candidate[0]>row_cut2 or candidate[1]<col_cut1 or candidate[1]>col_cut2]

                    if candidates_outside_box:
                        for position, idx_candidate in enumerate(candidates_outside_box):
                            if(
                            child.check_single_conflict(idx_candidate, (r, c)) or
                            child.check_single_conflict((r, c), idx_candidate) or
                            child.check_single_availability((r,c), idx_candidate[1]) or
                            child.check_single_availability(idx_candidate, c) or
                            child.check_single_lecturer((r,c), idx_candidate) or
                            child.check_single_lecturer(idx_candidate, (r,c))
                            ):
                                # If we can't swap it with the first candidate,
                                # we check the next one.
                                continue
                            else:
                                scores.append(child._delta_eval((r,c), idx_candidate))
                                positions.append(position)
                                # child.swap_courses(idx_candidate, (r,c))

                        if scores:
                            swap_counter += 1
                            best_score = scores.index(min(scores))
                            best_candidate_idx = positions[best_score]
                            child.swap_courses(candidates_outside_box[best_candidate_idx], (r,c))

            # print 'Number of swaps: ', swap_counter
            # print 'out of number of elements: ', max((row_cut2 - row_cut1), 1)*max((col_cut2 - col_cut1), 1)


        return offspring


    def mutation(self, Offspring):
        for Child in Offspring:
            child = Child.schedule
            probability_matrix = np.random.rand(child.shape[0], child.shape[1])
            mutation_idcs = np.where(probability_matrix <= self.mutation_prob)
            for room, ts in zip(mutation_idcs[0], mutation_idcs[1]):
                row = np.random.randint(0, child.shape[0])
                col = np.random.randint(0, child.shape[1])
                if (
                    Child.check_single_conflict((room,ts), (row,col)) or
                    Child.check_single_conflict((row, col), (room, ts)) or
                    Child.check_single_availability((row,col), ts) or
                    Child.check_single_availability((room, ts), col) or
                    Child.check_single_lecturer((row,col), (room, ts)) or
                    Child.check_single_lecturer((room, ts), (row,col))
                ):
                    continue

                Child.swap_courses((room, ts), (row, col))

        return Offspring


    def replacement(self):
        pass


    def print_population(self, individual, filename='first_output.sol'):
        with open(filename, 'w'): pass
        for course in self.data["courses"].keys():
            course_room, course_tslots = np.where(individual == int(course[1:]))
            days = [day/self.data['basics']['periods_per_day'] for day in course_tslots]
            periods = [day%self.data['basics']['periods_per_day'] for day in course_tslots]


            with open(filename, 'a') as outputfile:
                for day, period, room in zip(days, periods, course_room):
                    print >> outputfile, course, day, period, 'R'+'%04d' % room
