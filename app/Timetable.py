import numpy as np
from scipy.stats import itemfreq
import random


class Timetable(object):

    def __init__(self, data):
        self.data = data
        self.unscheduled = []
        self.score = -1
        self.schedule = np.zeros(shape=(data["basics"]["rooms"], data["basics"]["periods_per_day"] * data["basics"]["days"]), dtype=np.int8) - 1
        self.course_positions = dict((int(course[1:]),[]) for course in data["courses"].keys())

        self.compactness_p = 0
        self.room_p = 0
        self.capacity_p = 0
        self.min_wd_p = 0



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



    def fill_unscheduled(self):

        for unscheduled_course in self.unscheduled:
            for room,ts in self.course_positions[-1]:
                if(
                self.check_single_conflict(unscheduled_course, (room,ts), position=False) or
                self.check_single_availability(unscheduled_course, ts, position=False) or
                self.check_single_lecturer(unscheduled_course, (room,ts), position=False)
                ):
                    continue
                else:
                    self.swap_courses(unscheduled_course, (room,ts), position=False)
                    self.score -= 10
                    # print unscheduled_course
                    # print self.unscheduled
                    self.unscheduled.remove(unscheduled_course)
#                    if self.score != self.calc_score_total(save=False):
#                        print self.schedule
#                        print room,ts
#                        print 'diferencia de delta: ', self.score - self.calc_score_total(save=False)
                    break



    def room_hill_climb(self, room2swap=1, rndtry=1):

        num_rooms = self.schedule.shape[0]
        for col in range(self.schedule.shape[1]):
            for random_room in random.sample(range(0,num_rooms), room2swap):
#            for random_room in range(0,num_rooms):

                for random_try in range(0,rndtry):
                    room_to_swap = random.randint(0,num_rooms-1)
                    while(random_room == room_to_swap):
                        room_to_swap = random.randint(0,num_rooms-1)
    
                    if (self._capacity_delta((random_room,col), (room_to_swap,col))+self._room_delta((random_room,col), (room_to_swap,col))) < 0:
                        self.swap_courses((random_room,col), (room_to_swap,col))
                        break




    def insert_course(self, position, course):
        self.schedule[position] = course
        self.course_positions[course].append(position)


    def _delta_eval(self, pos_1, pos_2, position=True, swap=False):
        delta = []
        delta.append(self._capacity_delta(pos_1, pos_2, position))
        delta.append(self._compactness_delta(pos_1, pos_2, position))
        delta.append(self._min_days_delta(pos_1, pos_2, position))
        delta.append(self._room_delta(pos_1, pos_2, position))

        if swap:
            self.capacity_p += self._capacity_delta(pos_1, pos_2, position)
            self.compactness_p += self._compactness_delta(pos_1, pos_2, position)
            self.min_wd_p += self._min_days_delta(pos_1, pos_2, position)
            self.room_p += self._room_delta(pos_1, pos_2, position)

        return sum(delta)


    def swap_courses(self, pos_1, pos_2, position=True):

        total_delta = self._delta_eval(pos_1, pos_2, position, swap=True)
        # if total_delta < 0:
        self.score = self.score + total_delta

        if position:
            course_1 = self.schedule[pos_1]
        else:
            course_1 = pos_1
        course_2 = self.schedule[pos_2]

        if position:
            self.schedule[pos_1] = course_2
        self.schedule[pos_2] = course_1

        # if course_1 != -1:
        if position:
            self.course_positions[course_1].remove(pos_1)
        self.course_positions[course_1].append(pos_2)

        # if course_2 != -1:
        self.course_positions[course_2].remove(pos_2)
        if position:
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
            self.room_p = self._room_penalty()
            self.min_wd_p = self._min_days_penalty()
            self.capacity_p = self._capacity_penalty()
            self.compactness_p = self._compactness_penalty()

        else:
            return sum(penalty)





    def _capacity_delta(self, pos_1, pos_2, position=True):

        if position:
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
        else:
            # If we take an unscheduled course, the capacity delta can't improve.
            # It can only output 0 or penalty from excess of students.
            students_per_course_1 = self.data['students_per_course'][pos_1]
            capacity_2 = self.data['rooms'][pos_2[0]]
            return max(0, students_per_course_1 - capacity_2)


    def _min_days_delta(self, pos_1, pos_2, position=True):
        penalty = 5
        periods_per_day = self.data['basics']['periods_per_day']

        if position:
            course_1 = self.schedule[pos_1]
        else:
            course_1 = pos_1

        course_2 = self.schedule[pos_2]


        missing_days_before = 0
        missing_days_after  = 0
        course_1_positions = []
        course_2_positions = []
        if course_1 != -1:
            min_days_1 = self.data['min_days_per_course'][course_1]
            missing_days_before += max(0, min_days_1 - len(set([pos[1] // periods_per_day for pos in self.course_positions[course_1]])))
            course_1_positions = list(self.course_positions[course_1])
            if position:
                course_1_positions.remove(pos_1)

        if course_2 != -1:
            min_days_2 = self.data['min_days_per_course'][course_2]
            missing_days_before += max(0, min_days_2 - len(set([pos[1] // periods_per_day for pos in self.course_positions[course_2]])))
            course_2_positions = list(self.course_positions[course_2])
            course_2_positions.remove(pos_2)

        if position:
            course_2_positions.append(pos_1)
        course_1_positions.append(pos_2)

        if course_1 != -1:
            missing_days_after += max(0, min_days_1 - len(set([pos[1] // periods_per_day for pos in course_1_positions])))
        if course_2 != -1:
            missing_days_after += max(0, min_days_2 - len(set([pos[1] // periods_per_day for pos in course_2_positions])))

        return penalty * (missing_days_after - missing_days_before)



    def _compactness_delta(self, pos_1, pos_2, position=True):
        penalty = 2
        periods_per_day = self.data['basics']['periods_per_day']
        timeslots =  periods_per_day * self.data["basics"]["days"]

        if position:
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

        # If we are swapping an unscheduled course
        else:
            
            already_penalized = []
            unscheduled_curricula = [q for q in self.data['course_curricula'][pos_1]]
            value_after = 0
            day_bb = (pos_2[1] - 2) // periods_per_day
            day_b  = (pos_2[1] - 1) // periods_per_day
            day    =  pos_2[1] // periods_per_day
            day_a  = (pos_2[1] + 1) // periods_per_day
            day_aa = (pos_2[1] + 2) // periods_per_day
            
            if day_b == day:
                q_before = [qc for c in self.schedule[:, pos_2[1]-1] if c!=-1 for qc in self.data['course_curricula'][c]]
                for q in unscheduled_curricula:
                    if q in q_before:
                        if day_bb == day:
                            q_before2 = [qc for c in self.schedule[:, pos_2[1]-2] if c!=-1 for qc in self.data['course_curricula'][c]]
                            if q not in q_before2:
                                # In this case we fixed compactness in timeslots before
                                value_after -= 1
                        else:
                            value_after -= 1
                    else:
                        if day_a == day:
                            q_after = [qc for c in self.schedule[:, pos_2[1]+1] if c!=-1 for qc in self.data['course_curricula'][c]]
                            if q not in q_after:
                                value_after += 1
                                already_penalized.append(q)
                        else:
                            value_after += 1


            if day_a == day:
                q_after = [qc for c in self.schedule[:, pos_2[1]+1] if c!=-1 for qc in self.data['course_curricula'][c]]
                for q in unscheduled_curricula:
                    if q in q_after:
                        if day_aa == day:
                            q_after2 = [qc for c in self.schedule[:, pos_2[1]+2] if c!=-1 for qc in self.data['course_curricula'][c]]
                            if q not in q_after2:
                                # In this case we fixed compactness in timeslots after
                                value_after -= 1
                        else:
                            value_after -= 1
                    
                    else:
                        if day_b == day:
                            q_before = [qc for c in self.schedule[:, pos_2[1]-1] if c!=-1 for qc in self.data['course_curricula'][c]]
                            if q not in already_penalized and q not in q_before:
                                value_after += 1
                                
                        else:
                            value_after += 1

            
            return penalty * value_after







    def belong_same_day(self,ts_1, ts_2):
        return ts_1//self.data['basics']['periods_per_day'] == ts_2//self.data['basics']['periods_per_day']


    def _room_delta(self, pos_1, pos_2, position=True):

        if position:
            course_1 = self.schedule[pos_1]
        else:
            course_1 = pos_1
        course_2 = self.schedule[pos_2]

        num_rooms_before = 0
        course_1_positions = []
        course_2_positions = []

        if course_1 != -1:
            num_rooms_before += len(set([pos[0] for pos in self.course_positions[course_1]])) - 1
            course_1_positions = list(self.course_positions[course_1])
            if position:
                course_1_positions.remove(pos_1)

        if course_2 != -1:
            num_rooms_before += len(set([pos[0] for pos in self.course_positions[course_2]])) - 1
            course_2_positions = list(self.course_positions[course_2])
            course_2_positions.remove(pos_2)

        if position:
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


    def check_single_lecturer(self, pos_1, pos_2, position=True):
        individual = self.schedule
        # We check if we are passing a position or a course when
        # checking conflicts from unscheduled list
        if position:
            course = individual[pos_1]
        else:
            course = pos_1

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


    def check_single_conflict(self, pos_1, pos_2, position=True):
        individual = self.schedule
        # We check if we are passing a position or a course when
        # checking conflicts from unscheduled list
        if position==True:
            course = individual[pos_1]
        else:
            course = pos_1

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


    def check_single_availability(self, ind, timeslot, position=True):
        # We check if we are passing a position or a course when
        # checking conflicts from unscheduled list
        if position:
            course = self.schedule[ind]
        else:
            course = ind

        if course == -1:
            return False

        if timeslot in self.data["unavailable_slots"][course]:
            return True
        else:
            return False
