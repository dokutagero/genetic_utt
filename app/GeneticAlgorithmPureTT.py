# import GeneticAlgorithmBase
import numpy as np
import time

class GeneticAlgorithmPureTT():

    def __init__(self, data, population_size, mutation_prob):
        self.population_size = population_size
        self.mutation_prob = mutation_prob
        self.data = data

        # Create random initial population
        self.population = self.initialization(data["basics"]["rooms"],
                        data["basics"]["periods_per_day"] * data["basics"]["days"])

        self.print_population()


    def initialization(self, num_rooms, timeslots):
        population = []
        finish_time = time.time() + 60*1
        for i in range(self.population_size):
            individual = np.zeros(shape=(num_rooms, timeslots), dtype=np.int8) - 1
            idcs = [idcs for idcs, val in np.ndenumerate(individual)]
            np.random.shuffle(idcs)

            for course, course_info in self.data["courses"].iteritems():
                for num_lecture in range(course_info["number_of_lectures"]):
                    ind = idcs.pop()
                    individual[ind] = int(course[1:])

            idx_conflict = self.test_feasibility(individual)
            while idx_conflict != None:
                # if finish_time < time.time():
                #     population.append(individual)
                #     return population
                individual = self.random_swap(idx_conflict, individual)
                idx_conflict = self.test_feasibility(individual)

            population.append(individual)
        return population

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

    def random_swap(self, idx_conflict, individual):
        row = np.random.randint(0, individual.shape[0])
        col = np.random.randint(0, individual.shape[1])

        tmp = individual[(row,col)]
        individual[(row,col)] = individual[idx_conflict]
        # print 'miau'
        # print idx_conflict
        # print individual[idx_conflict]
        individual[idx_conflict] = tmp
        # print 'swapped'
        # print individual[:, idx_conflict[1]]
        return individual



    def test_feasibility(self, individual):

        # Unavailability
        for course, constraints in self.data["unavailability"].iteritems():
            course_no = int(course[1:])
            for idx in zip(constraints["day"], constraints["period"]):
                # print idx
                # print individual.shape
                conflict_timeslot = (self.data["basics"]["periods_per_day"])*idx[0]+idx[1]
                if course_no in individual[:,conflict_timeslot]:
                    # print course_no
                    # print individual[:, conflict_timeslot]
                    room_idx = np.where(individual[:, conflict_timeslot] == course_no)[0][0]
                    # print individual[room_idx, conflict_timeslot]
                    return (room_idx, conflict_timeslot)


        # Curricula
        for num_timeslot in range(individual.shape[1]):
            for curricula, courses in self.data["relations"].iteritems():
                # courses_tmp = courses
                row_curricula_conflict = []
                for course in courses:
                    # print 'holaaaaa'
                    # print courses
                    # print course[1:]
                    row_curricula_conflict.extend(np.where(individual[:,num_timeslot] == int(course[1:]))[0])
                    if len(row_curricula_conflict) > 1:
                        # print 'row curricula'
                        # print row_curricula_conflict[-1]
                        return (row_curricula_conflict[-1], num_timeslot)


    def print_population(self):

        for course in self.data["courses"].keys():
            course_room, course_tslots = np.where(self.population[0] == int(course[1:]))
            days = [day/6 for day in course_tslots]
            periods = [day%6 for day in course_tslots]


            with open('first_output.sol', 'a') as outputfile:
                for day, period, room in zip(days, periods, course_room):
                    print >> outputfile, course, day, period, 'R'+'%04d' % room
