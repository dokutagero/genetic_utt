# import GeneticAlgorithmBase
import numpy as np
import time
from collections import Counter
import FitnessFunctionTT as fftt
import random

class GeneticAlgorithmPureTT():

    def __init__(self, data, population_size, mutation_prob, fitness_model):
        self.population_size = population_size
        self.mutation_prob = mutation_prob
        self.data = data
        self.fitness_model = fitness_model

        # Create random initial population
        self.population = self.initialization(data["basics"]["rooms"],
                        data["basics"]["periods_per_day"] * data["basics"]["days"])

        # self.print_population()


    def genetic_simulation(self):

        # Population is already initialized from the constructor
        init_time = time.time()
        best_individual = self.fitness_model.get_best(self.population)
        iteration = 0
        print 'Best individual iteration ', iteration
        print self.fitness_model.evaluate(self.population[best_individual])
        while ((time.time() - init_time) < self.data["run_time"]):
            # Select 4 individuals randomly and return best of pairs
            p1, p2 = self.selection()
            o1, o2 = self.recombination(p1,p2)
            o1_prime, o2_prime = self.mutation((o1, o2))
            # Select 4 individuals and return worst of pairs
            w1, w2 = self.selection(best_selection=False)
            self.population[w1] = o1_prime
            self.population[w2] = o2_prime

            iteration += 1
        print 'Best individual iteration ', iteration
        print self.fitness_model.evaluate(self.population[best_individual])




    def initialization(self, num_rooms, timeslots):
        population = []
        time_start = time.time()

        iteration = 0
        # for i in range(self.population_size):
        while len(population) < self.population_size:
            individual = np.zeros(shape=(num_rooms, timeslots), dtype=np.int8) - 1
            idcs = [idcs for idcs, val in np.ndenumerate(individual)]
            np.random.shuffle(idcs)

            for course, course_info in self.data["courses"].iteritems():
                for num_lecture in range(course_info["number_of_lectures"]):
                    scheduled = False
                    i = 0

                    while not scheduled:
                        if i == len(idcs):
                            break
                        ind = idcs.pop(0)
                        course_id = int(course[1:])
                        if (
                            self.fitness_model.check_single_conflict(course_id, ind, individual, self_check=False) or
                            self.fitness_model.check_single_availability(course_id, ind[1]) or
                            self.fitness_model.check_single_lecturer(course_id, ind, individual, self_check=False)
                        ):
                            idcs.append(ind)
                            i += 1
                        else:
                            scheduled = True
                            individual[ind] = course_id

            population.append(individual)
        print time.time()-time_start

        return population


    def evaluation(self, individual):
        return self.fitness_model.evaluate(individual)


    def selection(self, best_selection=True):
        individual_indices = np.random.choice(range(len(self.population)), size=4, replace=False)
        fitness_values = [self.evaluation(self.population[individual]) for individual in individual_indices]

        if best_selection:
            return (individual_indices[fitness_values.index(min(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(min(fitness_values[2], fitness_values[3]))])
        else:
            return (individual_indices[fitness_values.index(max(fitness_values[0], fitness_values[1]))],
                    individual_indices[fitness_values.index(max(fitness_values[2], fitness_values[3]))])


    def recombination(self, parent1, parent2):

        # # Random cuts for columns
        # col_cut1, col_cut2 = sorted(random.sample(range(parent1.shape[1]), 2))
        # # Random cuts for rows
        # row_cut1, row_cut2 = sorted(random.sample(range(parent1.shape[0]), 2))
        parent1 = self.population[parent1]
        parent2 = self.population[parent2]

        row_cut1, row_cut2 = np.random.choice(range(parent1.shape[0]), size=2)
        col_cut1, col_cut2 = np.random.choice(range(parent1.shape[1]), size=2)

        # print "Column cuts: ", col_cut1, col_cut2
        # print "Row cuts: ", row_cut1, row_cut2

        offspring1 = np.copy(parent1)
        offspring2 = np.copy(parent2)

        offspring = [offspring1, offspring2]

        for child, parent in zip(offspring, [parent2, parent1]):
            for r in range(row_cut1, row_cut2 + 1):
                for c in range(col_cut1, col_cut2 + 1):
                    course2swap = parent[r,c]
                    ind = np.where(child == course2swap)

                    for r_prime, c_prime in zip(ind[0], ind[1]):
                        if (
                            self.fitness_model.check_single_conflict(child[r_prime, c_prime], (r, c), child, self_check=False) or
                            self.fitness_model.check_single_conflict(child[r, c], (r_prime,c_prime), child, self_check=False) or
                            self.fitness_model.check_single_availability(child[r,c], c_prime) or
                            self.fitness_model.check_single_availability(child[r_prime, c_prime], c) or
                            self.fitness_model.check_single_lecturer(child[r,c], (r_prime, c_prime), child, self_check=False) or
                            self.fitness_model.check_single_lecturer(child[r_prime, c_prime], (r,c), child, self_check=False)
                        ):
                            continue
                        else:
                            child = self.random_swap((r,c), (r_prime, c_prime), child)
                            break

        return offspring








    def mutation(self, offspring):
        for child in offspring:
            probability_matrix = np.random.rand(child.shape[0], child.shape[1])
            mutation_idcs = np.where(probability_matrix <= self.mutation_prob)
            for room, ts in zip(mutation_idcs[0], mutation_idcs[1]):
                row = np.random.randint(0, child.shape[0])
                col = np.random.randint(0, child.shape[1])
                if (
                    self.fitness_model.check_single_conflict(child[room,ts], (row,col), child, self_check=False) or
                    self.fitness_model.check_single_conflict(child[row, col], (room, ts), child, self_check=False) or
                    self.fitness_model.check_single_availability(child[row,col], ts) or
                    self.fitness_model.check_single_availability(child[room, ts], col) or
                    self.fitness_model.check_single_lecturer(child[row,col], (room, ts), child, self_check=False) or
                    self.fitness_model.check_single_lecturer(child[room, ts], (row,col), child, self_check=False)
                ):
                    continue

                child = self.random_swap((room, ts), (row, col), child)

        return offspring


        pass

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
