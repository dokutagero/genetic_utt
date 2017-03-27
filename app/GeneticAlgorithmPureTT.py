# import GeneticAlgorithmBase
import numpy as np
import time
from collections import Counter
import FitnessFunctionTT as fftt

class GeneticAlgorithmPureTT():

    def __init__(self, data, population_size, mutation_prob, fitness_model):
        self.population_size = population_size
        self.mutation_prob = mutation_prob
        self.data = data
        self.fitness_model = fitness_model

        # Create random initial population
        self.population = self.initialization(data["basics"]["rooms"],
                        data["basics"]["periods_per_day"] * data["basics"]["days"])

        self.print_population()


    def initialization(self, num_rooms, timeslots):
        population = []
        finish_time = time.time() + 60*3

        time_start = time.time()
        iteration = 0
        # for i in range(self.population_size):
        while len(population) < self.population_size:
            individual = np.zeros(shape=(num_rooms, timeslots), dtype=np.int8) - 1
            idcs = [idcs for idcs, val in np.ndenumerate(individual)]
            np.random.shuffle(idcs)

            for course, course_info in self.data["courses"].iteritems():
                for num_lecture in range(course_info["number_of_lectures"]):
                    ind = idcs.pop()
                    individual[ind] = int(course[1:])

            individual = self.randomize_individual(individual)
            if individual is None:
                continue

            population.append(individual)
        print time.time()-time_start
        return population

    def randomize_individual(self, individual):
        start_time = time.time()


        for i in range(individual.shape[0]):
            for j in range(individual.shape[1]):
                idx = (i,j)
                if (
                    self.fitness_model.check_single_conflict(individual[idx], idx, individual, self_check=True) or
                    self.fitness_model.check_single_availability(individual[idx], j) or
                    self.fitness_model.check_single_lecturer(individual[idx], idx, individual, self_check=True)
                ):


                    row = np.random.randint(0, individual.shape[0])
                    col = np.random.randint(0, individual.shape[1])
                    idx_conflict = idx
                    while(
                            self.fitness_model.check_single_conflict(individual[idx_conflict],(row,col), individual) or
                            self.fitness_model.check_single_conflict(individual[(row,col)], idx_conflict, individual) or
                            self.fitness_model.check_single_availability(individual[idx_conflict], col) or
                            self.fitness_model.check_single_availability(individual[(row,col)], idx_conflict[1]) or
                            self.fitness_model.check_single_lecturer(individual[idx_conflict], (row,col), individual) or
                            self.fitness_model.check_single_lecturer(individual[(row,col)], idx_conflict, individual)
                        ):
                        if time.time() - start_time > 0.5:
                            print "discarded..", i, j
                            return None

                        row = np.random.randint(0, individual.shape[0])
                        col = np.random.randint(0, individual.shape[1])

                    individual = self.random_swap(idx_conflict, (row,col), individual)

        return individual


    def evaluation(self, fitness_func):
        pass

    def selection(self):
        pass

    def recombination(self):
        pass

    def mutation(self):
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
                    # print "Lecturer conflict"
                    indx = np.nonzero(count)[0][0]
                    room_idx = np.where(individual[:,timeslot] == courses[indx])[0][0]

                    return (room_idx, timeslot)


    def print_population(self):
        with open('first_output.sol', 'w'): pass
        for course in self.data["courses"].keys():
            course_room, course_tslots = np.where(self.population[0] == int(course[1:]))
            days = [day/self.data['basics']['periods_per_day'] for day in course_tslots]
            periods = [day%self.data['basics']['periods_per_day'] for day in course_tslots]


            with open('first_output.sol', 'a') as outputfile:
                for day, period, room in zip(days, periods, course_room):
                    print >> outputfile, course, day, period, 'R'+'%04d' % room
