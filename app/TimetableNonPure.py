import numpy as np
from scipy.stats import itemfreq
from itertools import permutations
import random
from Timetable import Timetable

class TimetableNonPure(Timetable):

    def __init__(self, data):
        self.data = data
        self.unscheduled = []
        self.score = -1
        self.schedule = np.zeros(shape=(data["basics"]["rooms"], data["basics"]["periods_per_day"] * data["basics"]["days"]), dtype=np.int8) - 1
        self.course_positions = dict((int(course[1:]),[]) for course in data["courses"].keys())
        self.course_taught_in = dict((int(course[1:]),dict((room, 0) for room in range(data["basics"]['rooms']))) for course in data["courses"].keys())


        idcs = [idcs for idcs, val in np.ndenumerate(self.schedule)]
        # np.random.shuffle(idcs)

        courses = dict((int(course[1:]),0) for course in self.data['courses'].keys())
        for course, conflict in self.data["curric_conflict"].iteritems():
            tmp = 0
            for c in conflict:
                tmp +=  self.data['number_of_lectures'][c]
            # courses[course] = len(conflict)
            courses[course] = tmp

        courses_tuples = sorted(courses.items(), key=lambda x:x[1], reverse=True)
        # print courses_tuples
        # print idcs

        for course, val in courses_tuples:
            num_lectures = self.data['number_of_lectures'][course]
            for i in range(num_lectures):
                scheduled = False
                i = 0

                while not scheduled:
                    ind = idcs.pop(0)
                    # course_id = int(course[1:])

                    if i == len(idcs):
                        self.unscheduled.append(course)
                        break

                    if (
                        self.check_single_conflict_old_interface(course, ind) or
                        self.check_single_availability_old_interface(course, ind) or
                        self.check_single_lecturer_old_interface(course, ind)
                    ):
                        idcs.append(ind)
                        i += 1
                    else:
                        scheduled = True
                        self.insert_course(ind, course)

        # self._find_empty_slots()
        self.calc_score_total()
        self.optimize_timeslots(3)




    # def insert_unscheduled(self):
    #     empty_slots = self.course_positions[-1]
    #
    #     print self.unscheduled
    #
    #     for course in self.unscheduled:
    #         for pos in empty_slots:
    #             if (
    #                 self.check_single_conflict_old_interface(course, pos) or
    #                 self.check_single_availability_old_interface(course, pos) or
    #                 self.check_single_lecturer_old_interface(course, pos)
    #             ):
    #                 continue
    #             else:
    #                 self.insert_course(pos, course)
    #
    #     # TODO DOESN'T SEEM TO BE DOING ANYTHING...
    #     print self.unscheduled

    # hill climber
    def optimize_timeslots(self, iterations='random', timeslots='all'):
      Timetable.optimize_timeslots(self, iterations, timeslots)

    def _find_empty_slots(self):
        Timetable._find_empty_slots(self)

    def insert_course(self, position, course):
        Timetable.insert_course(self, position, course)

    def _delta_eval(self, pos_1, pos_2):
        return Timetable._delta_eval(self, pos_1, pos_2)

    def swap_courses(self, pos_1, pos_2):
        Timetable.swap_courses(self, pos_1, pos_2)

    def calc_score_total(self, save=True, print_out=False):
        penalty = Timetable.calc_score_total(self, False, print_out)

        if save:
            self.score = penalty
        else:
            return penalty


    def _capacity_delta_ts(self, ts, order):
        return Timetable._capacity_delta_ts(self, ts, order)

    def _room_delta_ts(self, ts, order):
        return Timetable._room_delta_ts(self, ts, order)

    def _capacity_delta(self, pos_1, pos_2):
        return Timetable._capacity_delta(self, pos_1, pos_2)

    def _min_days_delta(self, pos_1, pos_2):
        return Timetable._min_days_delta(self, pos_1, pos_2)

    def _compactness_delta(self, pos_1, pos_2):
        return Timetable._compactness_delta(self, pos_1, pos_2)

    def _room_delta(self, pos_1, pos_2):
        return Timetable._room_delta(self, pos_1, pos_2)

    def _unscheduled_penalty(self):
        return Timetable._unscheduled_penalty(self)

    def _capacity_penalty(self):
        return Timetable._capacity_penalty(self)

    def _min_days_penalty(self):
        return Timetable._min_days_penalty(self)

    def _compactness_penalty(self):
        return Timetable._compactness_penalty(self)

    def _room_penalty(self):
        return Timetable._room_penalty(self)

    def check_single_lecturer_old_interface(self, course, pos):
        return Timetable.check_single_lecturer_old_interface(self, course, pos)

    def check_single_lecturer(self, pos_1, pos_2):
        return Timetable.check_single_lecturer(self, pos_1, pos_2)

    def check_single_conflict_old_interface(self, course, pos):
        return Timetable.check_single_conflict_old_interface(self, course, pos)

    def check_single_conflict(self, pos_1, pos_2):
        return Timetable.check_single_conflict(self, pos_1, pos_2)

    def check_single_availability_old_interface(self, course, pos):
        return Timetable.check_single_availability_old_interface(self, course, pos)

    def check_single_availability(self, ind, timeslot):
        return Timetable.check_single_availability(self, ind, timeslot)
