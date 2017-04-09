import numpy as np
from scipy.stats import itemfreq


class Timetable(object):

    def __init__(self, data):
        self.data = data
        self.unscheduled = []
        self.score = -1
        self.schedule = np.zeros(shape=(data["basics"]["rooms"], data["basics"]["periods_per_day"] * data["basics"]["days"]), dtype=np.int8) - 1
        self.course_positions = dict((int(course[1:]),[]) for course in data["courses"].keys())

        idcs = [idcs for idcs, val in np.ndenumerate(self.schedule)]
        np.random.shuffle(idcs)

        for course, course_info in self.data["courses"].iteritems():
            for num_lecture in range(course_info["number_of_lectures"]):
                scheduled = False
                i = 0

                while not scheduled:
                    ind = idcs.pop(0)
                    course_id = int(course[1:])

                    if i == len(idcs):
                        self.unscheduled.append(course_id)
                        break

                    if (
                        self.check_single_conflict_self(course_id, ind) or
                        self.check_single_availability_self(course_id, ind) or
                        self.check_single_lecturer_self(course_id, ind)
                    ):
                        idcs.append(ind)
                        i += 1
                    else:
                        scheduled = True
                        self.insert_course(ind, course_id, True)

        self._calc_score_total()


    def insert_course(self, position, course, init=False):
        self.schedule[position] = course
        self.course_positions[course].append(position)


    def _delta_eval(self, pos_1, pos_2):
        delta = []
        delta.append(self._capacity_delta(pos_1, pos_2))
        delta.append(self._compactness_delta(pos_1, pos_2))
        delta.append(self._min_days_delta(pos_1, pos_2))
        delta.append(self._room_delta(pos_1, pos_2))

        return sum(delta)


    def swap_courses(self, pos_1, pos_2):
        self._delta_eval(pos_1, pos_2)

        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        self.schedule[pos_1] = course_2
        self.schedule[pos_2] = course_1

        if course_1 != -1:
            self.course_positions[course_1].remove(pos_1)
            self.course_positions[course_1].append(pos_2)

        if course_2 != -1:
            self.course_positions[course_2].remove(pos_2)
            self.course_positions[course_2].append(pos_1)


    def _calc_score_total(self):
        penalty = []
        penalty.append(self._unscheduled_penalty())
        penalty.append(self._capacity_penalty())
        penalty.append(self._min_days_penalty())
        penalty.append(self._compactness_penalty())
        penalty.append(self._room_penalty())

        self.score = sum(penalty)


    def _capacity_delta(self, pos_1, pos_2):
        capacity_1 = self.data['rooms'][pos_1[0]]
        capacity_2 = self.data['rooms'][pos_2[0]]

        if self.schedule[pos_1] != -1:
            students_per_course_1 = self.data['students_per_course'][self.schedule[pos_1]]
        else:
            students_per_course_1 = 0

        if self.schedule[pos_2] != -1:
            students_per_course_2 = self.data['students_per_course'][self.schedule[pos_2]]
        else:
            students_per_course_2 = 0

        before = max(0, students_per_course_1 - capacity_1) + max(0, students_per_course_2 - capacity_2)
        after  = max(0, students_per_course_2 - capacity_1) + max(0, students_per_course_1 - capacity_2)

        return after - before


    def _min_days_delta(self, pos_1, pos_2):
        penalty = 5
        periods_per_day = self.data['basics']['periods_per_day']

        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        # TODO
        # WE NEED TO ADD A CHECK IF course_1 and coures_2 are not -1

        num_days_1_before = len(set([pos[1] // periods_per_day for pos in self.course_positions[course_1]]))
        num_days_2_before = len(set([pos[1] // periods_per_day for pos in self.course_positions[course_2]]))

        course_1_positions = list(self.course_positions[course_1])
        course_2_positions = list(self.course_positions[course_2])

        course_1_positions.remove(pos_1)
        course_1_positions.append(pos_2)
        course_2_positions.remove(pos_2)
        course_2_positions.append(pos_1)

        num_days_1_after = len(set([pos[1] // periods_per_day for pos in course_1_positions]))
        num_days_2_after = len(set([pos[1] // periods_per_day for pos in course_2_positions]))

        return penalty * (num_days_1_after + num_days_2_after - num_days_1_before - num_days_2_before)


    def _compactness_delta(self, pos_1, pos_2):
        penalty = 2
        periods_per_day = self.data['basics']['periods_per_day']
        timeslots =  self.data["basics"]["periods_per_day"] * self.data["basics"]["days"]

        curricula_1 = []
        curricula_2 = []
        if self.schedule[pos_1] != -1:
            curricula_1 = self.data['course_curricula'][self.schedule[pos_1]]
        if self.schedule[pos_2] != -1:
            curricula_2 = self.data['course_curricula'][self.schedule[pos_2]]

        curricula_list = [curricula_1, curricula_2]
        pos_list = [pos_1, pos_2]

        value_before = 0
        value_after = 0

        # _bb - before before
        # _b  - before
        #
        # _a  - after
        # _aa - after after

        for pos, curricula in zip(pos_list, curricula_list):
            day_bb = pos[1] - 2 // periods_per_day if pos[1] - 2 >= 0 else -1
            day_b  = pos[1] - 1 // periods_per_day if pos[1] - 1 >= 0 else -1
            day    = pos[1] // periods_per_day
            day_a  = pos[1] + 1 // periods_per_day if pos[1] + 1 < timeslots else -1
            day_aa = pos[1] + 2 // periods_per_day if pos[1] + 2 < timeslots else -1

            # Check timeslot before
            if day_b == day:
                curricula_b  = [self.data["course_curricula"][course] for course in self.schedule[:,pos1[1]-1]]

                if day_bb == day:
                    curricula_bb = [self.data["course_curricula"][course] for course in self.schedule[:,pos1[1]-2]]

                    for curriculum in curricula:
                        if curriculum in curricula_b:
                            if curriculum not in curricula_bb:
                                # if curriculum is in day_b but not in day_bb we seclude the course
                                value_before += 1
                else:
                    for curriculum in curricula:
                        if curriculum in curricula_b:
                            # if curriculum is in day_b we seclude it for sure
                            value_before += 1


            #  Check timeslot after
            if day_a == day:
                curricula_a  = [self.data["course_curricula"][course] for course in self.schedule[:,pos[1]+1]]

                if day_aa == day:
                    curricula_aa = [self.data["course_curricula"][course] for course in self.schedule[:,pos[1]+2]]

                    for curriculum in curricula:
                        if curriculum in curricula_a:
                            if curriculum not in curricula_aa:
                                # if curriculum is in day_a but not in day_bb we seclude the course
                                value_before += 1
                else:
                    for curriculum in curricula:
                        if curriculum in curricula_a:
                            # if curriculum is in day_a we seclude it for sure
                            value_before += 1


        # simulate swap
        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        schedule_copy = self.schedule.copy()
        schedule_copy[pos_1] = course_2
        schedule_copy[pos_2] = course_1

        curricula_1 = []
        curricula_2 = []
        if schedule_copy[pos_1] != -1:
            curricula_1 = self.data['course_curricula'][schedule_copy[pos_1]]
        if schedule_copy[pos_2] != -1:
            curricula_2 = self.data['course_curricula'][schedule_copy[pos_2]]

        curricula_list = [curricula_1, curricula_2]
        pos_list = [pos_1, pos_2]


        for pos, curricula in zip(pos_list, curricula_list):

            day_bb = pos[1]-2 // periods_per_day if pos[1] - 2 >= 0 else -1
            day_b  = pos[1]-1 // periods_per_day if pos[1] - 1 >= 0 else -1
            day    = pos[1] // periods_per_day
            day_a  = pos[1]+1 // periods_per_day if pos[1] + 1 < timeslots else -1
            day_aa = pos[1]+2 // periods_per_day if pos[1] + 2 < timeslots else -1

            # Check timeslot before
            if day_b == day:
                curricula_b  = [self.data["course_curricula"][course] for course in self.schedule[:,pos1[1]-1]]

                if day_bb == day:
                    curricula_bb = [self.data["course_curricula"][course] for course in self.schedule[:,pos1[1]-2]]

                    for curriculum in curricula:
                        if curriculum in curricula_b:
                            if curriculum not in curricula_bb:
                                # if curriculum is in day_b but not in day_bb we seclude the course
                                value_after += 1
                else:
                    for curriculum in curricula:
                        if curriculum in curricula_b:
                            # if curriculum is in day_b we seclude it for sure
                            value_after += 1


            #  Check timeslot after
            if day_a == day:
                curricula_a  = [self.data["course_curricula"][course] for course in self.schedule[:,pos[1]+1]]

                if day_aa == day:
                    curricula_aa = [self.data["course_curricula"][course] for course in self.schedule[:,pos[1]+2]]

                    for curriculum in curricula:
                        if curriculum in curricula_a:
                            if curriculum not in curricula_aa:
                                # if curriculum is in day_a but not in day_bb we seclude the course
                                value_after += 1
                else:
                    for curriculum in curricula:
                        if curriculum in curricula_a:
                            # if curriculum is in day_a we seclude it for sure
                            value_after += 1


        return value_after - value_before


    def _room_delta(self, pos_1, pos_2):
        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        num_rooms_before = len(set([pos[0] for pos in self.course_positions[course_1]])) + len(set([pos[0] for pos in self.course_positions[course_2]]))

        course_1_positions = list(self.course_positions[course_1])
        course_2_positions = list(self.course_positions[course_2])

        course_1_positions.remove(pos_1)
        course_1_positions.append(pos_2)
        course_2_positions.remove(pos_2)
        course_2_positions.append(pos_1)

        num_rooms_after = len(set([pos[0] for pos in course_1_positions])) + len(set([pos[0] for pos in course_2_positions]))

        return num_rooms_after - num_rooms_before



    def _unscheduled_penalty(self):
        """
        Each course has a predetermined amount of lectures that must
        be given. As many of these lectures as possible must be sched-
        uled. Each course that has a lecture which is not scheduled gives
        a penalty of 10 points.

        A whole individual is checked in order to calculate the penalty
        """

        individual = self.schedule
        penalty = 10
        value = 0

        occurrences_scheduled = dict((entry[0], entry[1]) for entry in itemfreq(individual.flatten()))
        occurrences_desired   = dict((int(course[1:]), info["number_of_lectures"]) for (course,info) in self.data["courses"].iteritems())

        for key in occurrences_desired:
            value += occurrences_desired[key]
            if key in occurrences_scheduled:
                value -= occurrences_scheduled[key]

        return value * penalty

    def _capacity_penalty(self):
        """
        For each lecture, the number of students that attend the course
        must be less or equal than the number of seats of all the rooms
        that host its lectures. Each student above the capacity counts as
        1 point of penalty.

        A whole individual is checked in order to calculate the penalty
        """

        individual = self.schedule
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

    def _min_days_penalty(self):
        """
        The lectures of each course must be spread into a given minimum
        number of days. Each day below the minimum counts as 5 points
        of penalty.

        A whole individual is checked in order to calculate the penalty
        """

        individual = self.schedule

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

        return value * penalty


    def _compactness_penalty(self):
        """
        Lectures belonging to a curriculum should be adjacent to each
        other (i.e., in consecutive time slots). For a given curriculum we
        call a lecture from the curriculum secluded if it is not scheduled
        adjacent to any other lecture from the same curriculum within
        the same day. Each secluded lecture in a curriculum counts as 2
        points of penalty.

        A whole individual is checked in order to calculate the penalty
        """

        individual = self.schedule
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



    def _room_penalty(self):
        """
        All lectures of a course should be given in the same room. Each
        distinct room used for the lectures of a course, but the intrst, counts
        as 1 point of penalty.

        A whole individual is checked in order to calculate the penalty
        """

        individual = self.schedule
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


    def check_single_lecturer_self(self, course, pos):
        individual = self.schedule

        if course == -1:
            return False

        lecturers_in_slot = [l for c in individual[:,pos[1]] if c!=-1 and c!=course for l in self.data["lecturer_lecture"][c] ]

        if self.data["lecturer_lecture"][course][0] in lecturers_in_slot:
            return True
        else:
            return False


    def check_single_lecturer(self, pos_1, pos_2):
        individual = self.schedule
        course = individual[pos_1]

        if course == -1:
            return False

        lecturers_in_slot = [l for c in individual[:,pos_2[1]] if c!=-1 for l in self.data["lecturer_lecture"][c] ]

        if self.data["lecturer_lecture"][course][0] in lecturers_in_slot:
            return True
        else:
            return False


    def check_single_conflict_self(self, course, pos):
        individual = self.schedule

        if course == -1:
            return False

        course_conflicts = self.data["curric_conflict"][course]
        if len([c for c in individual[:,pos[1]] if c in course_conflicts])>1:
            return True
        else:
            return False


    def check_single_conflict(self, pos_1, pos_2):
        individual = self.schedule
        course = individual[pos_1]

        if course == -1:
            return False

        course_conflicts = self.data["curric_conflict"][course]
        for c in individual[:,pos_2[1]]:
            if c in course_conflicts:
                return True

        return False


    def check_single_availability_self(self, course, pos):
        timeslot = pos[1]

        if course == -1:
            return False

        if timeslot in self.data["unavailable_slots"][course]:
            return True
        else:
            return False


    def check_single_availability(self, ind, timeslot):
        course = self.schedule[ind]

        if course == -1:
            return False

        if timeslot in self.data["unavailable_slots"][course]:
            return True
        else:
            return False
