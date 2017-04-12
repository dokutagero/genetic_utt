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
                        self.check_single_conflict_old_interface(course_id, ind) or
                        self.check_single_availability_old_interface(course_id, ind) or
                        self.check_single_lecturer_old_interface(course_id, ind)
                    ):
                        idcs.append(ind)
                        i += 1
                    else:
                        scheduled = True
                        self.insert_course(ind, course_id)

        rooms, tss = np.where(self.schedule == -1)
        self.course_positions[-1] = []
        for room,ts in zip(rooms, tss):
            self.course_positions[-1].append((room,ts))

        self.calc_score_total()


    def insert_course(self, position, course):
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

        total_delta = self._delta_eval(pos_1, pos_2)
        # if total_delta < 0:
        self.score = self.score + total_delta

        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        self.schedule[pos_1] = course_2
        self.schedule[pos_2] = course_1

        # if course_1 != -1:
        self.course_positions[course_1].remove(pos_1)
        self.course_positions[course_1].append(pos_2)

        # if course_2 != -1:
        self.course_positions[course_2].remove(pos_2)
        self.course_positions[course_2].append(pos_1)



    def calc_score_total(self, save=True):
        penalty = []
        penalty.append(self._unscheduled_penalty())
        penalty.append(self._capacity_penalty())
        penalty.append(self._min_days_penalty())
        penalty.append(self._compactness_penalty())
        penalty.append(self._room_penalty())

        if save:
            self.score = sum(penalty)
        else:
            return sum(penalty)


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


        missing_days_before = 0
        missing_days_after  = 0
        course_1_positions = []
        course_2_positions = []
        if course_1 != -1:
            min_days_1 = self.data['min_days_per_course'][course_1]
            missing_days_before += max(0, min_days_1 - len(set([pos[1] // periods_per_day for pos in self.course_positions[course_1]])))
            course_1_positions = list(self.course_positions[course_1])
            course_1_positions.remove(pos_1)

        if course_2 != -1:
            min_days_2 = self.data['min_days_per_course'][course_2]
            missing_days_before += max(0, min_days_2 - len(set([pos[1] // periods_per_day for pos in self.course_positions[course_2]])))
            course_2_positions = list(self.course_positions[course_2])
            course_2_positions.remove(pos_2)

        course_2_positions.append(pos_1)
        course_1_positions.append(pos_2)

        if course_1 != -1:
            missing_days_after += max(0, min_days_1 - len(set([pos[1] // periods_per_day for pos in course_1_positions])))
        if course_2 != -1:
            missing_days_after += max(0, min_days_2 - len(set([pos[1] // periods_per_day for pos in course_2_positions])))

        return penalty * (missing_days_after - missing_days_before)



    def _compactness_delta(self, pos_1, pos_2):
        penalty = 2
        periods_per_day = self.data['basics']['periods_per_day']
        timeslots =  periods_per_day * self.data["basics"]["days"]

        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        curricula_1 = set()
        curricula_2 = set()

        if course_1 != -1:
            curricula_1 = set(self.data["course_curricula"][course_1])
        if course_2 != -1:
            curricula_2 = set(self.data["course_curricula"][course_2])
        courses_courricula = curricula_1.union(curricula_2)

        already_penalized = []

        value_before = 0
        value_after = 0

        '''
            _bb - before before
            _b  - before
            _c  - current
            _a  - after
            _aa - after after
        '''

        if course_1 != course_2:
            positions = [pos_1, pos_2]

            for pos in positions:
                day_bb = (pos[1] - 2) // periods_per_day
                day_b  = (pos[1] - 1) // periods_per_day
                day    =  pos[1] // periods_per_day
                day_a  = (pos[1] + 1) // periods_per_day
                day_aa = (pos[1] + 2) // periods_per_day

                curricula_bb = []
                curricula_b  = []
                curricula_a  = []
                curricula_aa = []

                if day_b == day:
                    curricula_b = [curr for course in self.schedule[:,pos[1]-1] if course != -1 for curr in self.data["course_curricula"][course]]
                if day_bb == day:
                    curricula_bb = [curr for course in self.schedule[:,pos[1]-2] if course != -1 for curr in self.data["course_curricula"][course]]

                if day_a == day:
                    curricula_a = [curr for course in self.schedule[:,pos[1]+1] if course != -1 for curr in self.data["course_curricula"][course]]
                if day_aa == day:
                    curricula_aa = [curr for course in self.schedule[:,pos[1]+2] if course != -1 for curr in self.data["course_curricula"][course]]

                curricula_c = [curr for course in self.schedule[:,pos[1]] if course != -1 for curr in self.data["course_curricula"][course]]

                for curriculum in courses_courricula:
                    if (pos[1] - 1, curriculum) not in already_penalized and curriculum in curricula_b and curriculum not in curricula_c and curriculum not in curricula_bb:
                        value_before += 1
                        already_penalized.append((pos[1] - 1, curriculum))

                    if (pos[1] , curriculum) not in already_penalized and curriculum in curricula_c and curriculum not in curricula_b and curriculum not in curricula_a:
                        value_before += 1
                        already_penalized.append((pos[1] , curriculum))

                    if (pos[1] + 1, curriculum) not in already_penalized and curriculum in curricula_a and curriculum not in curricula_c and curriculum not in curricula_aa:
                        value_before += 1
                        already_penalized.append((pos[1] + 1, curriculum))

            # simulate swap
            schedule_copy = np.array(self.schedule)
            schedule_copy[pos_1] = course_2
            schedule_copy[pos_2] = course_1

            already_penalized = []

            for pos in positions:

                day_bb = (pos[1] - 2) // periods_per_day
                day_b  = (pos[1] - 1) // periods_per_day
                day    =  pos[1] // periods_per_day
                day_a  = (pos[1] + 1) // periods_per_day
                day_aa = (pos[1] + 2) // periods_per_day

                curricula_bb = []
                curricula_b  = []
                curricula_a  = []
                curricula_aa = []

                if day_b == day:
                    curricula_b = [curr for course in schedule_copy[:,pos[1]-1] if course != -1 for curr in self.data["course_curricula"][course]]
                if day_bb == day:
                    curricula_bb = [curr for course in schedule_copy[:,pos[1]-2] if course != -1 for curr in self.data["course_curricula"][course]]

                if day_a == day:
                    curricula_a = [curr for course in schedule_copy[:,pos[1]+1] if course != -1 for curr in self.data["course_curricula"][course]]
                if day_aa == day:
                    curricula_aa = [curr for course in schedule_copy[:,pos[1]+2] if course != -1 for curr in self.data["course_curricula"][course]]

                curricula_c = [curr for course in schedule_copy[:,pos[1]] if course != -1 for curr in self.data["course_curricula"][course]]

                for curriculum in courses_courricula:
                    if (pos[1] - 1, curriculum) not in already_penalized and curriculum in curricula_b and curriculum not in curricula_c and curriculum not in curricula_bb:
                        value_after += 1
                        already_penalized.append((pos[1] - 1, curriculum))

                    if (pos[1] , curriculum) not in already_penalized and curriculum in curricula_c and curriculum not in curricula_b and curriculum not in curricula_a:
                        value_after += 1
                        already_penalized.append((pos[1] , curriculum))

                    if (pos[1] + 1, curriculum) not in already_penalized and curriculum in curricula_a and curriculum not in curricula_c and curriculum not in curricula_aa:
                        value_after += 1
                        already_penalized.append((pos[1] + 1, curriculum))


        return penalty * ( value_after - value_before)
        # penalty = 2
        # value_after = 0
        # value_before = 0
        #
        # curric_pos1 = []
        # curric_pos2 = []
        # if self.schedule[pos_1] != -1:
        #     curric_pos1 = [q for q in self.data['course_curricula'][self.schedule[pos_1]]]
        # if self.schedule[pos_2] != -1:
        #     curric_pos2 = [q for q in self.data['course_curricula'][self.schedule[pos_2]]]
        # # Unique curricula for both courses to swap.
        # # Empty if both courses are -1
        # curric_list = set(curric_pos1 + curric_pos2)
        #
        #
        # already_penalized = []
        # # Check penalty before swap
        # for room,ts in [pos_1, pos_2]:
        #     # True/false vector determining if previos and post ts belong to same days
        #     day_limits = [self.belong_same_day(ts, ts_prime) for ts_prime in [ts-2, ts-1, ts, ts+1, ts+2]]
        #     for q in curric_list:
        #         already_paid = False
        #         q_ts = [qc for c in self.schedule[:,(ts)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #         # If previous and next day are within same day and within matrix limits
        #         if day_limits[2-1]:
        #             q_ts_previous = [qc for c in self.schedule[:,(ts-1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #             if q not in q_ts and q in q_ts_previous:
        #                 # If two ts before within same day and within matrix limits
        #                 if day_limits[2-2]:
        #                     q_ts_previous2 = [qc for c in self.schedule[:,(ts-2)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     if q not in q_ts_previous2:
        #                         if (ts-1, q) not in already_penalized:
        #                             value_before += 1
        #                             already_penalized.append((ts-1,q))
        #                 else:
        #                     #paguem
        #                     if (ts-1, q) not in already_penalized:
        #                         value_before += 1
        #                         already_penalized.append((ts-1,q))
        #             elif q in q_ts and q not in q_ts_previous:
        #                 if day_limits[2+1]:
        #                     q_ts_post = [qc for c in self.schedule[:,(ts+1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     if q not in q_ts_post:
        #                         if (ts,q) not in already_penalized:
        #                             value_before += 1
        #                             #already_paid = True
        #                             already_penalized.append((ts,q))
        #                 else:
        #                     if (ts,q) not in already_penalized:
        #                         value_before += 1
        #                         already_penalized.append((ts,q))
        #
        #         if day_limits[2+1]:
        #             q_ts_post = [qc for c in self.schedule[:,(ts+1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #             if q not in q_ts and q in q_ts_post:
        #                 if day_limits[2+2]:
        #                     q_ts_post2 = [qc for c in self.schedule[:,(ts+2)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     if q not in q_ts_post2:
        #                         if (ts+1,q) not in already_penalized:
        #                             value_before += 1
        #                             already_penalized.append((ts+1,q))
        #                 else:
        #                     if (ts+1,q) not in already_penalized:
        #                         value_before += 1
        #                         already_penalized.append((ts+1,q))
        #
        #             elif q in q_ts and q not in q_ts_post:
        #                 if day_limits[2-1]:
        #                     q_ts_previous = [qc for c in self.schedule[:,(ts-1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     # if not already_paid:
        #                     if q not in q_ts_previous:# and not already_paid:
        #                         if (ts,q) not in already_penalized:
        #                             value_before += 1
        #                             already_penalized.append((ts,q))
        #                 else:
        #                     if (ts,q) not in already_penalized:
        #                         value_before += 1
        #                         already_penalized.append((ts,q))
        #
        #
        #
        # tt_copy = np.copy(self.schedule)
        # tmp = tt_copy[pos_1]
        # tt_copy[pos_1] = self.schedule[pos_2]
        # tt_copy[pos_2] = tmp
        #
        # already_penalized = []
        # # Check penalty after swap
        # for room,ts in [pos_1, pos_2]:
        #     # True/false vector determining if previos and post ts belong to same days
        #     day_limits = [self.belong_same_day(ts, ts_prime) for ts_prime in [ts-2, ts-1, ts, ts+1, ts+2]]
        #     for q in curric_list:
        #         already_paid = False
        #         q_ts = [qc for c in tt_copy[:,(ts)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #         # If previous and next day are within same day and within matrix limits
        #         if day_limits[2-1]:
        #             q_ts_previous = [qc for c in tt_copy[:,(ts-1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #             if q not in q_ts and q in q_ts_previous:
        #                 # If two ts before within same day and within matrix limits
        #                 if day_limits[2-2]:
        #                     q_ts_previous2 = [qc for c in tt_copy[:,(ts-2)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     if q not in q_ts_previous2:
        #                         if (ts-1, q) not in already_penalized:
        #                             value_after += 1
        #                             already_penalized.append((ts-1,q))
        #                 else:
        #                     #paguem
        #                     if (ts-1, q) not in already_penalized:
        #                         value_after += 1
        #                         already_penalized.append((ts-1,q))
        #
        #             elif q in q_ts and q not in q_ts_previous:
        #                 if day_limits[2+1]:
        #                     q_ts_post = [qc for c in tt_copy[:,(ts+1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     if q not in q_ts_post:
        #                         if (ts, q) not in already_penalized:
        #                             value_after += 1
        #                             already_penalized.append((ts,q))
        #                             #already_paid = True
        #                 else:
        #                     if (ts,q) not in already_penalized:
        #                         value_after += 1
        #                         already_penalized.append((ts,q))
        #
        #         if day_limits[2+1]:
        #             q_ts_post = [qc for c in tt_copy[:,(ts+1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #             if q not in q_ts and q in q_ts_post:
        #                 if day_limits[2+2]:
        #                     q_ts_post2 = [qc for c in tt_copy[:,(ts+2)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     if q not in q_ts_post2:
        #                         if (ts+1,q) not in already_penalized:
        #                             value_after += 1
        #                             already_penalized.append((ts+1,q))
        #                 else:
        #                     if (ts+1,q) not in already_penalized:
        #                         value_after += 1
        #                         already_penalized.append((ts+1,q))
        #
        #             elif q in q_ts and q not in q_ts_post:
        #                 if day_limits[2-1]:
        #                     q_ts_previous = [qc for c in tt_copy[:,(ts-1)] if c!=-1 for qc in self.data['course_curricula'][c]]
        #                     # if not already_paid:
        #                     if q not in q_ts_previous:# and not already_paid:
        #                         if (ts,q) not in already_penalized:
        #                             value_after += 1
        #                             already_penalized.append((ts,q))
        #                 else:
        #                     if (ts,q) not in already_penalized:
        #                         value_after += 1
        #                         already_penalized.append((ts,q))
        #
        #
        # return penalty * (value_after - value_before)

    def belong_same_day(self,ts_1, ts_2):
        return ts_1//self.data['basics']['periods_per_day'] == ts_2//self.data['basics']['periods_per_day']


    def _room_delta(self, pos_1, pos_2):
        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        num_rooms_before = 0
        course_1_positions = []
        course_2_positions = []

        if course_1 != -1:
            num_rooms_before += len(set([pos[0] for pos in self.course_positions[course_1]])) - 1
            course_1_positions = list(self.course_positions[course_1])
            course_1_positions.remove(pos_1)

        if course_2 != -1:
            num_rooms_before += len(set([pos[0] for pos in self.course_positions[course_2]])) - 1
            course_2_positions = list(self.course_positions[course_2])
            course_2_positions.remove(pos_2)

        course_2_positions.append(pos_1)
        course_1_positions.append(pos_2)

        num_rooms_after = 0
        if course_1 != -1:
            num_rooms_after += len(set([pos[0] for pos in course_1_positions])) - 1
        if course_2 != -1:
            num_rooms_after += len(set([pos[0] for pos in course_2_positions])) - 1

        return  num_rooms_after - num_rooms_before


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


    def check_single_lecturer_old_interface(self, course, pos):
        if course == -1:
            return False

        lecturers_in_slot = [l for c in self.schedule[:,pos[1]] if c!=-1 for l in self.data["lecturer_lecture"][c] ]

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


    def check_single_conflict_old_interface(self, course, pos):
        if course == -1:
            return False

        course_conflicts = self.data["curric_conflict"][course]
        for c in self.schedule[:,pos[1]]:
            if c in course_conflicts:
                return True

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


    def check_single_availability_old_interface(self, course, pos):
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
