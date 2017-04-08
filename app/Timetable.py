import numpy as np

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
                        self.check_single_conflict(course_id, ind, self_check=False) or
                        self.check_single_availability(course_id, ind[1]) or
                        self.check_single_lecturer(course_id, ind, self_check=False)
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

        if init:
            delta = self._delta_eval(pos_1, pos_2)

    def _delta_eval(self, pos_1, pos_2):
        delta = []
        delta.append(self._unscheduled_delta())
        delta.append(self._capacity_delta(pos_1, pos_2))
        delta.append(self._compactness_delta())
        delta.append(self._min_days_delta())
        delta.append(self._room_delta(pos_1, pos_2))

        return sum(delta)


    def swap_courses(self, pos_1, pos_2):
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
        penalty.append(self.unscheduled_penalty(individual))
        penalty.append(self.capacity_penalty(individual))
        penalty.append(self.min_days_penalty(individual))
        penalty.append(self.compactness_penalty(individual))
        penalty.append(self.room_penalty(individual))

        self.score = sum(penalty)

    def _capacity_delta(self, pos_1, pos_2):
        capacity_1 = self.data['rooms'][pos_1[0]]
        capacity_2 = self.data['rooms'][pos_2[0]]

        students_per_course_1 = self.data['students_per_course'][self.schedule[pos_1]]
        students_per_course_2 = self.data['students_per_course'][self.schedule[pos_2]]

        before = max(0, students_per_course_1 - capacity_1) + max(0, students_per_course_2 - capacity_2)
        after  = max(0, students_per_course_2 - capacity_1) + max(0, students_per_course_1 - capacity_2)

        return after - before

    def _min_days_delta(self):
        pass

    def _compactness_delta(self):
        pass

    def _room_delta(self, pos_1, pos_2):
        course_1 = self.schedule[pos_1]
        course_2 = self.schedule[pos_2]

        num_rooms_before = len(set([pos[0] for pos in self.course_positions[course_1]])) + len(set([pos[0] for pos in self.course_positions[course_2]]))

        coures_1_positions = list(self.course_positions[coures_1])
        coures_2_positions = list(self.course_positions[coures_2])

        coures_1_positions.remove(pos_1)
        coures_1_positions.append(pos_2)
        coures_2_positions.remove(pos_2)
        coures_2_positions.append(pos_1)

        num_rooms_after = len(set([pos[0] for pos in coures_1_positions])) + len(set([pos[0] for pos in coures_2_positions]))

        return num_rooms_after - num_rooms_before

    def _capacity_delta(self):
        pass

    def _unscheduled_delta(self):
        pass


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


    def check_single_lecturer(self, pos_1, pos_2, self_check=False):
        individual = self.schedule
        course = individual[pos_1]

        if course == -1:
            return False

        lecturers_in_slot = [l for c in individual[:,pos_2[1]] if c!=-1 for l in self.data["lecturer_lecture"][c] ]

        if self_check == True:
            lecturers_in_slot = [l for c in individual[:,pos_2[1]] if c!=-1 and c!=course for l in self.data["lecturer_lecture"][c] ]

        if self.data["lecturer_lecture"][course][0] in lecturers_in_slot:
            return True
        else:
            return False


    def check_single_conflict(self, pos_1, pos_2, self_check=False):
        individual = self.schedule
        course = individual[pos_1]

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


    def check_single_availability(self, ind, timeslot):
        course = self.schedule[ind]

        if course == -1:
            return False

        if timeslot in self.data["unavailable_slots"][course]:
            return True
        else:
            return False
