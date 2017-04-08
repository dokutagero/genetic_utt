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


    def genetic_simulation(self):
        init_time = time.time()
        iteration = 0

        while ((time.time() - init_time) < self.data["run_time"]):
            # Select 4 individuals randomly and return best of pairs
            p1, p2 = self.selection()
            o1, o2 = self.recombination(self.population[p1], self.population[p2])
            o1_prime, o2_prime = self.mutation((o1, o2))
            # Select 4 individuals and return worst of pairs
            w1, w2 = self.selection(best_selection=False)
            self.population[w1] = o1_prime
            self.population[w2] = o2_prime

            iteration += 1
        #print 'Best individual iteration ', iteration
        best_individual = self.fitness_model.get_best(self.population)
        # print 'BEEEEEEEEEST'
        # print self.fitness_model.evaluate(self.population[best_individual])
        self.print_population(self.population[best_individual])
        print 'Iterations : ' , iteration



    def initialize_population(self):
        for i in xrange(self.population_size):
            Individual = Timetable(self.data)
            self.population.append(Individual)


    def evaluation(self, Individual):
        return self.fitness_model.evaluate(Individual)


    def selection(self, best_selection=True):
        individual_indices = np.random.choice(range(len(self.population)), size=4, replace=False)
        pdb.set_trace()
        fitness_values = [self.population[ind].score for ind in individual_indices]
        # fitness_values = [self.evaluation(self.population[individual]) for individual in individual_indices]

        if best_selection:
            return (individual_indices[fitness_values.index(min(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(min(fitness_values[2], fitness_values[3]))])
        else:
            return (individual_indices[fitness_values.index(max(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(max(fitness_values[2], fitness_values[3]))])


    def recombination(self, Parent1, Parent2):
        # We obtain the random 2D cuts for each parent.
        row_cut1, row_cut2 = np.random.choice(range(Parent1.schedule.shape[0]), size=2)
        col_cut1, col_cut2 = np.random.choice(range(Parent1.schedule.shape[1]), size=2)

        # Before performing the PMX crossover, the offspring is equal to the parents.
        offspring1 = copy.deepcopy(Parent1)
        offspring2 = copy.deepcopy(Parent2)

        offspring = [offspring1, offspring2]

        # offspring1 is copy of Parent2 and offspring2 is copy of Parent1
        # This is the reason of having them in opposite orders in the next for.
        for child, parent in zip(offspring, [Parent2, Parent1]):
            for r in range(row_cut1, row_cut2 + 1):
                for c in range(col_cut1, col_cut2 + 1):
                    parent_course2swap = parent.schedule[r,c]
                    child_course2swap = child.schedule[r,c]

                    idcs_child_candidates = child.course_positions[parent_course2swap]
                    # If there are scheduled courses.
                    if idcs_child_candidates:
                        for position, idx_candidate in enumerate(idcs_child_candidates):
                            if(
                            child.check_single_conflict(idx_candidate, (r, c), self_check=False) or
                            child.check_single_conflict((r, c), idx_candidate, self_check=False) or
                            child.check_single_availability((r,c), idx_candidate[1]) or
                            child.check_single_availability(idx_candidate, c) or
                            child.check_single_lecturer((r,c), idx_candidate, self_check=False) or
                            child.check_single_lecturer(idx_candidate, (r,c), self_check=False)
                            ):
                                # If we can't swap it with the first candidate,
                                # we check the next one.
                                continue
                            else:
                                child.swap_courses(idx_candidate, (r,c))


        return offspring

        # for child, parent in zip(offspring, [parent2, parent1]):
        #     for r in range(row_cut1, row_cut2 + 1):
        #         for c in range(col_cut1, col_cut2 + 1):
        #             course2swap = parent[r,c]
        #             ind = np.where(child == course2swap)
        #
        #             for r_prime, c_prime in zip(ind[0], ind[1]):
        #                 if (
        #                     self.fitness_model.check_single_conflict(child[r_prime, c_prime], (r, c), child, self_check=False) or
        #                     self.fitness_model.check_single_conflict(child[r, c], (r_prime,c_prime), child, self_check=False) or
        #                     self.fitness_model.check_single_availability(child[r,c], c_prime) or
        #                     self.fitness_model.check_single_availability(child[r_prime, c_prime], c) or
        #                     self.fitness_model.check_single_lecturer(child[r,c], (r_prime, c_prime), child, self_check=False) or
        #                     self.fitness_model.check_single_lecturer(child[r_prime, c_prime], (r,c), child, self_check=False)
        #                 ):
        #                     continue
        #                 else:
        #                     child = self.random_swap((r,c), (r_prime, c_prime), child)
        #                     break
        #
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
                    Child.check_single_conflict((room,ts), (row,col), self_check=False) or
                    Child.check_single_conflict((row, col), (room, ts), self_check=False) or
                    Child.check_single_availability((row,col), ts) or
                    Child.check_single_availability((room, ts), col) or
                    Child.check_single_lecturer((row,col), (room, ts), self_check=False) or
                    Child.check_single_lecturer((room, ts), (row,col), self_check=False)
                ):
                    continue

                Child.swap_courses((room, ts), (row, col))

        return Offspring


    def replacement(self):
        pass

    def random_swap(self, idx_conflict, idx_swap, individual):
        #row = np.random.randint(0, individual.shape[0])
        #col = np.random.randint(0, individual.shape[1])

        tmp = individual[idx_swap]
        individual[idx_swap] = individual[idx_conflict]
        individual[idx_conflict] = tmp

        return individual



# TODO DO ONLY ALLOWED SWAPS -----------> Doesn't seem to work very well <-----------
        # row = np.random.randint(0, individual.shape[0])
        # col = np.random.randint(0, individual.shape[1])
        #
        # copy = deepcopy(individual)
        # copy[(row,col)] = individual[idx_conflict]
        # copy[idx_conflict] = individual[(row,col)]
        #
        # idx_conflict = self.test_feasibility(copy)
        # while idx_conflict is not None:
        #     row = np.random.randint(0, individual.shape[0])
        #     col = np.random.randint(0, individual.shape[1])
        #
        #     copy = deepcopy(individual)
        #     copy[(row,col)] = individual[idx_conflict]
        #     copy[idx_conflict] = individual[(row,col)]
        #     idx_conflict = self.test_feasibility(copy)
        #
        # individual[(row,col)] = copy[idx_conflict]
        # individual[idx_conflict] = copy[(row,col)]
        #
        # return individual



    def test_feasibility(self, individual):


        res = self.fitness_model.check_availability_constraint(individual)
        if res is not None:
            return res
        # # Unavailability
        # for course, constraints in self.data["unavailability"].iteritems():
        #     course_no = int(course[1:])
        #     for idx in zip(constraints["day"], constraints["period"]):
        #         conflict_timeslot = (self.data["basics"]["periods_per_day"])*idx[0]+idx[1]
        #         if course_no in individual[:,conflict_timeslot]:
        #             # print "Unavailability conflict"
        #             room_idx = np.where(individual[:, conflict_timeslot] == course_no)[0][0]
        #             return (room_idx, conflict_timeslot)


        res = self.fitness_model.check_conflicts_constraint(individual)
        if res is not None:
            return res
        # # Curricula
        # for timeslot in range(individual.shape[1]):
        #     timeslot_courses = individual[:,timeslot]
        #
        #     for curriculum, courses in self.data["relations"].iteritems():
        #         count = Counter(timeslot_courses)
        #         count = [count[int(course[1:])] for course in courses]
        #         if sum(count) > 1:
        #             # print "Curricula conflict"
        #             indx = np.nonzero(count)[0][0]
        #             room_idx = np.where(individual[:,timeslot] == int(courses[indx][1:]))[0][0]
        #
        #             return (room_idx, timeslot)


        # lecturers
        lecturers_courses = {}

        for course, info in self.data["courses"].iteritems():
            lecturer = info["lecturer"]

            if lecturer in lecturers_courses:
                lecturers_courses[lecturer].append(int(course[1:]))
            else:
                lecturers_courses[lecturer] = [int(course[1:])]

        for timeslot in range(individual.shape[1]):
            timeslot_courses = individual[:,timeslot]

            for lecturer, courses in lecturers_courses.iteritems():
                count = Counter(timeslot_courses)
                count = [count[course] for course in courses]

                if sum(count) > 1:
                    indx = np.nonzero(count)[0][0]
                    room_idx = np.where(individual[:,timeslot] == courses[indx])[0][0]

                    return (room_idx, timeslot)


    def print_population(self, individual, filename='first_output.sol'):
        with open(filename, 'w'): pass
        for course in self.data["courses"].keys():
            course_room, course_tslots = np.where(individual == int(course[1:]))
            days = [day/self.data['basics']['periods_per_day'] for day in course_tslots]
            periods = [day%self.data['basics']['periods_per_day'] for day in course_tslots]


            with open(filename, 'a') as outputfile:
                for day, period, room in zip(days, periods, course_room):
                    print >> outputfile, course, day, period, 'R'+'%04d' % room
