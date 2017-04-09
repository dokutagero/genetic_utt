from FitnessFunctionBase import FitnessFunctionBase
from collections import Counter
import numpy as np
from scipy.stats import itemfreq
import copy
import operator
from functools import reduce

class FitnessFunctionTT(FitnessFunctionBase):

    def __init__(self, data):
        super(FitnessFunctionTT, self).__init__(data)

    def evaluate(self, individual):
        penalty = []
        penalty.append(self.unscheduled_penalty(individual))
        penalty.append(self.capacity_penalty(individual))
        penalty.append(self.min_days_penalty(individual))
        penalty.append(self.compactness_penalty(individual))
        penalty.append(self.room_penalty(individual))

        for name, p in zip(["unscheduled", "capacity", "min_days", "compactness", "room"], penalty):
            print name, ':', p

        return sum(penalty)

    def check_hard_constraints(self):
        pass

    def check_soft_constraints(self):
        pass

    def unscheduled_penalty(self, individual):
        """
        Each course has a predetermined amount of lectures that must
        be given. As many of these lectures as possible must be sched-
        uled. Each course that has a lecture which is not scheduled gives
        a penalty of 10 points.

        A whole individual is checked in order to calculate the penalty

        Args:
            individual (ndarray): Individual representation.


        Returns:
            penalty:   The penalty for not scheduling all the lectures for some courses
        """

        penalty = 10
        value = 0

        occurrences_scheduled = dict((entry[0], entry[1]) for entry in itemfreq(individual.flatten()))
        occurrences_desired   = dict((int(course[1:]), info["number_of_lectures"]) for (course,info) in self.data["courses"].iteritems())

        for key in occurrences_desired:
            value += occurrences_desired[key]
            if key in occurrences_scheduled:
                value -= occurrences_scheduled[key]

        return value * penalty

    def unscheduled_delta(self, individual, slot, course_position):

        penalty = 10
        value = 0
        room = slot[0]
        tslot = slot[1]
        course = individual[room, tslot]

        value = self.data['courses'][course]['number_of_lectures']-len(course_position[course])
        return value*penalty


    def capacity_penalty(self, individual):
        """
        For each lecture, the number of students that attend the course
        must be less or equal than the number of seats of all the rooms
        that host its lectures. Each student above the capacity counts as
        1 point of penalty.

        A whole individual is checked in order to calculate the penalty

        Args:
            individual (ndarray): Individual representation.


        Returns:
            penalty:   The penalty for scheduling lectures in not big enough rooms
        """

        penalty = 1
        value = 0
        all_rooms = self.data['rooms']
        students_per_course = self.data['students_per_course']

        for room in range(0, len(individual[:,0])):
            for slot in range(0, len(individual[0,:])):
                course = individual[room, slot]
                if course != -1:
                    value += max(0, students_per_course[course] - all_rooms[room])

        return value * penalty


    def min_days_penalty(self, individual):
        """
        The lectures of each course must be spread into a given minimum
        number of days. Each day below the minimum counts as 5 points
        of penalty.

        A whole individual is checked in order to calculate the penalty

        Args:
            individual (ndarray): Individual representation.


        Returns:
            penalty:   The penalty for not spreading the course over minimum number of days
        """

        penalty = 5
        value = 0
        periods_per_day = self.data['basics']['periods_per_day']
        working_days = self.data['basics']['days']
        courses =  self.data['basics']['courses']

        scheduled = np.zeros((courses, working_days))
        for slot in range(0, len(individual[0,:])):
            day = slot // periods_per_day

            for room in range(0, len(individual[:,0])):
                course = individual[room, slot]

                if course != -1:
                    scheduled[course, day] = 1

        courses = self.data["courses"]
        days_desired = dict((int(course[1:]), info["minimum_working_days"]) for (course,info) in courses.iteritems())

        for key in days_desired:
            value += max(0, days_desired[key] - sum(scheduled[key,:]))

        # Actually slower than above
        # values = 0
        # for course, info in courses.iteritems():
        #     values += max(0, info['minimum_working_days'] - sum(scheduled[course[1:],:]))

        return value * penalty


    def min_days_delta(self, individual, slot1, slot2, course_position):

        penalty = 5
        value_before = 0
        value_after = 0
        room = [slot1[0],slot2[0]]
        tslot = [slot1[1],slot2[1]]
        courses = [individual[room[0], tslot[0]],individual[room[1],tslot[1]]]
        periods = []
        periods_per_day = self.data['basics']['periods_per_day']
        for i in range(2):
            for pos in course_position[courses[i]]:
                periods[i,pos].append(pos[1] // periods_per_day)
            value_before += self.data['courses'][courses[i]]['minimum_working_days']-len(set(periods[i,:]))

        course_position_copy = dict(course_position)
        course_position_copy[courses[0]].remove(slot1)
        course_position_copy[courses[0]].append(slot2)
        course_position_copy[courses[1]].remove(slot2)
        course_position_copy[courses[1]].append(slot1)

        periods = []
        periods_per_day = self.data['basics']['periods_per_day']
        for i in range(2):
            for pos in course_position_copy[courses[i]]:
                periods[i,pos].append(pos[1] // periods_per_day)
            value_after += self.data['courses'][courses[i]]['minimum_working_days']-len(set(periods[i,:]))

        return penalty*max(0,value_after-value_before)



    def compactness_penalty(self, individual):
        """
        Lectures belonging to a curriculum should be adjacent to each
        other (i.e., in consecutive time slots). For a given curriculum we
        call a lecture from the curriculum secluded if it is not scheduled
        adjacent to any other lecture from the same curriculum within
        the same day. Each secluded lecture in a curriculum counts as 2
        points of penalty.

        A whole individual is checked in order to calculate the penalty

        Args:
            individual (ndarray): Individual representation.


        Returns:
            penalty:   The penalty for not having compactness for courses in curricula
        """

        penalty = 2

        periods_per_day = self.data['basics']['periods_per_day']
        no_ts = len(individual[0,:])
        no_rooms = len(individual[:,0])

        secluded = dict()
        for i in range(0, no_rooms):
            for j in range(0, no_ts):
                course = individual[i,j]
                if course != -1:
                    curricula = self.data["course_curricula"][course]
                    secluded[(i,j)] = {'curricula': list(curricula), 'copy': curricula}
                else:
                    secluded[(i,j)] = {'curricula': [], 'copy': []}

        for slot in range(0, (no_ts-1)):
            if (slot // periods_per_day) == ((slot+1) // periods_per_day):

                for i in range(0, no_rooms):
                    course = individual[i,slot]

                    if course != -1:
                        curricula_copy = secluded[i,slot]['copy']
                        for curriculum in curricula_copy:
                            for j in range(0, no_rooms):
                                curricula_next_copy = secluded[j,(slot+1)]['copy']

                                if curriculum in curricula_next_copy:
                                    curricula_working = secluded[i,slot]['curricula']
                                    curricula_next_working = secluded[j,(slot+1)]['curricula']
                                    if curriculum in curricula_working:
                                        secluded[i,slot]['curricula'].remove(curriculum)
                                    if curriculum in curricula_next_working:
                                        secluded[j,(slot+1)]['curricula'].remove(curriculum)

        value = sum([len(curricula['curricula']) for curricula in secluded.values()])

        return value * penalty
        """
        cube = np.ones((individual.shape[0], individual.shape[1], max(self.data["curricula"].iteritems(), key=operator.itemgetter(1))[1])) * -2

        for row in range(individual.shape[0]):
            for col in range(individual.shape[1]):
                if individual[row,col] != -1:
                    for idx,curriculum in enumerate(self.data["course_curricula"][individual[row,col]]):
                        cube[row,col,idx] = curriculum

        secluded_counter = 0
        # First column
        col2_union = reduce(np.union1d, cube[:,1,:])
        for idx in range(individual.shape[0]):
            course_unique = set(cube[idx,0,:])
            intersec = np.intersect1d(course_unique, col2_union)
            secluded_counter += len(course_unique) - len(intersec)

        # Middle columns
        for col in range(1, individual.shape[1] - 1):
            previous_col_union = reduce(np.union1d, cube[:,col-1,:])
            next_col_union = reduce(np.union1d, cube[:,col+1,:])
            col_union = np.union1d(previous_col_union, next_col_union)

            for idx in range(individual.shape[0]):
                course_unique = set(cube[idx,col,:])
                intersec = np.intersect1d(course_unique, col_union)
                secluded_counter += len(course_unique) - len(intersec)

        # Last column
        penultimate_col_union = reduce(np.union1d, cube[:,-2,:])
        for idx in range(individual.shape[0]):
            course_unique = set(cube[idx,-1,:])
            intersec = np.intersect1d(course_unique, penultimate_col_union)
            secluded_counter += len(course_unique) - len(intersec)

        return secluded_counter * penalty """



    def room_penalty(self, individual):
        """
        All lectures of a course should be given in the same room. Each
        distinct room used for the lectures of a course, but the intrst, counts
        as 1 point of penalty.

        A whole individual is checked in order to calculate the penalty

        Args:
            individual (ndarray): Individual representation.


        Returns:
            penalty:   The penalty for using more than one room per course
        """

        penalty = 1
        value = 0
        courses = self.data['courses']
        schedule = {}

        for room in range(0, len(individual[:,0])):
            for slot in range(0, len(individual[0,:])):
                course = individual[room, slot]

                if course != -1:
                    if schedule.has_key(course):
                        schedule[course].append(room)
                    else:
                        schedule[course] = [room]

        value = sum([(len(np.unique(rooms))-1) for rooms in schedule.values()])
        return value * penalty


    def check_lectures_constraint(self):
        """
        Each course has a predetermined amount of lectures. Each lecture must be
        scheduled in distinct time slots and the total number of lectures cannot
        be exceeded.

        A whole individual is checked in order to determine if the condition
        stated above is fulfilled. In case that a gene of the individual
        violates such condition, the index is returned.

        Args:
            individual (ndarray): Individual representation.


        Returns:
            (row(int), col(int)):   Indices of the conflict in the individual if
                                    constraint is violated.

                            None:    If there is no conflict in the individual.
        """
        pass


    def check_single_lecturer(self,course, idx, individual, self_check=False):
        if course == -1:
            return False

        lecturers_in_slot = [l for c in individual[:,idx[1]] if c!=-1 for l in self.data["lecturer_lecture"][c] ]

        if self_check == True:
            lecturers_in_slot = [l for c in individual[:,idx[1]] if c!=-1 and c!=course for l in self.data["lecturer_lecture"][c] ]

        if self.data["lecturer_lecture"][course][0] in lecturers_in_slot:
            return True
        else:
            return False


    def check_room_occupancy_constraint(self):
        """
        Two lectures cannot take place in the same room in the same time slot.

        A whole individual is checked in order to determine if the condition
        stated above is fulfilled. In case that a gene of the individual
        violates such condition, the index is returned.

        Args:
            individual (ndarray): Individual representation.


        Returns:
            (row(int), col(int)):   Indices of the conflict in the individual if
                                    constraint is violated.

                            None:    If there is no conflict in the individual.
        """
        pass

    def check_conflicts_constraint(self, individual):
        """
        Lectures of courses in the same curriculum or taught by the same
        lecturer must all be scheduled in different time slots.

        A whole individual is checked in order to determine if the condition
        stated above is fulfilled. In case that a gene of the individual
        violates such condition, the index is returned.

        Args:
            individual (ndarray): Individual representation.


        Returns:
            (row(int), col(int)):   Indices of the conflict in the individual if
                                    constraint is violated.

                            None:    If there is no conflict in the individual.
        """
        relations = self.data["relations"]
        for timeslot in range(individual.shape[1]):
            timeslot_courses = individual[:,timeslot]

            for curriculum, courses in relations.iteritems():
                count = Counter(timeslot_courses)
                count = [count[int(course[1:])] for course in courses]
                if sum(count) > 1:
                    indx = np.nonzero(count)[0][0]
                    room_idx = np.where(individual[:,timeslot] == int(courses[indx][1:]))[0][0]

                    return (room_idx, timeslot)


    def check_single_conflict(self, course, idx, individual, self_check=False):
        if course == -1:
            return False

        course_conflicts = self.data["curric_conflict"][course]
        if self_check == True:
            if len([c for c in individual[:,idx[1]] if c in course_conflicts])>1:
                return True
        else:
            for c in individual[:,idx[1]]:
                if c in course_conflicts:
                    return True

        return False

    def check_availability_constraint(self, individual):
        """
        Some courses cannot be scheduled at specific time slots.

        A whole individual is checked in order to determine if the condition
        stated above is fulfilled. In case that a gene of the individual
        violates such condition, the index is returned.

        Args:
            individual (ndarray): Individual representation.


        Returns:
            (row(int), col(int)):   Indices of the conflict in the individual if
                                    constraint is violated.

                            None:    If there is no conflict in the individual.
        """
        periods_per_day = self.data["basics"]["periods_per_day"]

        for course, constraints in self.data["unavailability"].iteritems():
            course_no = int(course[1:])
            for timeslot_tuple in zip(constraints["day"], constraints["period"]):
                # self.check_single_availability(course, timeslot_tuple, individual)
                conflict_timeslot = periods_per_day*timeslot_tuple[0]+timeslot_tuple[1]
                if course_no in individual[:,conflict_timeslot]:
                    # print "Unavailability conflict"
                    room_idx = np.where(individual[:, conflict_timeslot] == course_no)[0][0]
                    return (room_idx, conflict_timeslot)


    def check_single_availability(self, course, timeslot):
        if course == -1:
            return False

        if timeslot in self.data["unavailable_slots"][course]:
            return True
        else:
            return False


    def get_best(self, population):
        fitness_values = [self.evaluate(individual) for individual in population]
        return fitness_values.index(min(fitness_values))
