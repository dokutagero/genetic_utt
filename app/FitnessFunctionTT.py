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


    def check_single_lecturer(self,course, idx, individual):
        # If same lecturer in same slot returns False
        if course == -1:
            return False

        lecturers_in_slot = [l for c in individual[:,idx[1]] if c!=-1 for l in self.data["lecturer_lecture"][c] ]
        print 'TEEEEEEST'
        print lecturers_in_slot
        print self.data["lecturer_lecture"][course]
        #elif self.data["lecturer_lecture"][course] in [l for c,l in self.data["lecturer_lecture"][individual[idx]] if c != course]:
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
                    # print "Curricula conflict"
                    indx = np.nonzero(count)[0][0]
                    room_idx = np.where(individual[:,timeslot] == int(courses[indx][1:]))[0][0]

                    return (room_idx, timeslot)


    def check_single_conflict(self, course, idx, individual):
        # If given course is repeated in same timeslot or has other currical subs
        # returns False
        print individual[:,idx[1]]
        # if len([c for c in individual[:,idx[1]] if c == course])>0:
            # return True
        if course == -1:
            return False

        course_conflicts = self.data["curric_conflict"][course]
        print course_conflicts
        for c in individual[:,idx[1]]:
            if c in course_conflicts:
                print 'FUCKING TRUE'

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


    def check_single_availability(self,course, timeslot_tup):
        # Returns False if problem
        # print timeslot_tup
        if course == -1:
            return False
        if (timeslot_tup[1]) in self.data["unavailable_slots"][course]:
            return True
        else:
            return False
