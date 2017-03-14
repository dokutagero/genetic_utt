from FitnessFunctionBase import FitnessFunctionBase
from collections import Counter
import numpy as np


class FitnessFunctionTT(FitnessFunctionBase):

    def __init__(self, data):
        super(FitnessFunctionTT, self).__init__(data)

    def evaluate(self):
        pass

    def check_hard_constraints(self):
        pass

    def check_soft_constraints(self):
        pass

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
                    # print "Curricula conflict"
                    indx = np.nonzero(count)[0][0]
                    room_idx = np.where(individual[:,timeslot] == int(courses[indx][1:]))[0][0]

                    return (room_idx, timeslot)
        pass

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


    def check_single_availability(self,course, timeslot_tup):
        if (timeslot_tup[0]*6 + timeslot_tup[1]) in data["unavailable_slots"][course]:
            return False
