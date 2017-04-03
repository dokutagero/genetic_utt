from FitnessFunctionBase import FitnessFunctionBase
from collections import Counter
import numpy as np
from scipy.stats import itemfreq
import pandas as pd
import copy

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

        for val in penalty:
            print val

        print sum(penalty)


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
        courses   = self.data['courses']
        courses_names = self.data['course_str']

        for room in np.arange(len(individual[:,0])):
            capacity = all_rooms[room]

            for slot in np.arange(len(individual[0,:])):
                course = individual[room, slot]
                if course != -1:
                    number_of_students = courses[courses_names[course]]['number_of_students']
                    value += max(0, number_of_students - capacity)

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
        for slot in np.arange(len(individual[0,:])):
            day = slot // periods_per_day

            for room in np.arange(len(individual[:,0])):
                course = individual[room, slot]

                if course != -1:
                    scheduled[course, day] = 1

        days_desired = dict((int(course[1:]), info["minimum_working_days"]) for (course,info) in self.data["courses"].iteritems())

        for key in days_desired:
            value += max(0, days_desired[key] - sum(scheduled[key,:]))

        return value * penalty


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
        for i in np.arange(no_rooms):
            for j in np.arange(no_ts):
                course = individual[i,j]
                if course != -1:
                    curricula = self.data["course_curricula"][course]
                    secluded[(i,j)] = {'curricula': copy.deepcopy(curricula), 'copy': copy.deepcopy(curricula)}
                else:
                    secluded[(i,j)] = {'curricula': [], 'copy': []}

        for slot in np.arange((no_ts-1)):
            if (slot // periods_per_day) == ((slot+1) // periods_per_day):

                for i in np.arange(no_rooms):
                    course = individual[i,slot]

                    if course != -1:
                        curricula_copy = secluded[i,slot]['copy']
                        for curriculum in curricula_copy:
                            for j in np.arange(no_rooms):
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


    def room_penalty(self, individual):
        """
        All lectures of a course should be given in the same room. Each
        distinct room used for the lectures of a course, but the rst, counts
        as 1 point of penalty.

        A whole individual is checked in order to calculate the penalty

        Args:
            individual (ndarray): Individual representation.


        Returns:
            penalty:   The penalty for using more than one room per course
        """

        penalty = 1
        value = 0
        courses   = self.data['courses']
        schedule = {}

        for room in np.arange(len(individual[:,0])):
            for slot in np.arange(len(individual[0,:])):
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
        for timeslot in range(individual.shape[1]):
            timeslot_courses = individual[:,timeslot]

            for curriculum, courses in self.data["relations"].iteritems():
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

        for course, constraints in self.data["unavailability"].iteritems():
            course_no = int(course[1:])
            for timeslot_tuple in zip(constraints["day"], constraints["period"]):
                # self.check_single_availability(course, timeslot_tuple, individual)
                conflict_timeslot = (self.data["basics"]["periods_per_day"])*timeslot_tuple[0]+timeslot_tuple[1]
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
