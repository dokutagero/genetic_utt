import csv
directory = "UniversityTimetablingCompetition"

def load(params, index=5):
	index = '%02d' % index
	global path
	path = directory + '/Test' + index + '/'
	data = {}
	data["run_time"] = int(params[-1])
	data["basics"] = (load_basics(params[0]))
	data["courses"] = (load_courses(params[1]))
	data["lecturers"] = (load_lecturers(params[2]))
	data["rooms"] = (load_rooms(params[3]))
	data["curricula"] = (load_curriculas(params[4]))
	data["relations"] = (load_relations(params[5]))
	data["unavailability"] = (load_unavailability(params[6]))
	text_to_int_courses(data)
	unavailability_slots(data)
	students_per_course(data)
	curricula_conflicts(data)
	lecturer_lectures(data)
	course_curriculum(data)
	min_days_per_course(data)
	return data

def students_per_course(data):
	data['students_per_course'] = {}
	courses = data['courses']
	for course in data["courses"].keys():
		data["students_per_course"][int(course[1:])] = courses[course]['number_of_students']

def min_days_per_course(data):
	data['min_days_per_course'] = {}
	courses = data['courses']
	for course in data["courses"].keys():
		data["min_days_per_course"][int(course[1:])] = courses[course]['minimum_working_days']

def text_to_int_courses(data):
	data["course_int"] = {}
	data["course_str"] = {}
	for course_name in data["courses"].keys():
		data["course_int"][course_name] = int(course_name[1:])
		data["course_str"][int(course_name[1:])] = course_name


def unavailability_slots(data):
	data["unavailable_slots"] = {}
	for course in data["course_str"].keys():
		data["unavailable_slots"][course] = []

	for course, unav in data["unavailability"].iteritems():
		# data["unavailable_slots"][data["course_int"][course]] = []
		for day, period in zip(unav['day'], unav['period']):
			data["unavailable_slots"][data["course_int"][course]].append(day*data['basics']['periods_per_day'] + period)

def curricula_conflicts(data):
	data["curric_conflict"] = {}
	for curricula, courses in data["relations"].iteritems():
		for course in courses:
			if data["curric_conflict"].has_key(int(course[1:])):
				data["curric_conflict"][int(course[1:])] = data["curric_conflict"][int(course[1:])].union(set([int(c[1:]) for c in courses]))
			else:
				data["curric_conflict"][int(course[1:])] = set([int(c[1:]) for c in courses])

def course_curriculum(data):
	data["course_curricula"] = {}
	for curriculum, courses in data["relations"].iteritems():
		curriculum = int(curriculum[1:])

		for course in courses:
			course = int(course[1:])
			if data["course_curricula"].has_key(course):
				data["course_curricula"][course].append(curriculum)
			else:
				data["course_curricula"][course] = [curriculum]

def lecturer_lectures(data):
	data["lecturer_lecture"] = {}

	for course, info in data["courses"].iteritems():
		if data["course_int"][course] not in data["lecturer_lecture"].keys():
			data["lecturer_lecture"][data["course_int"][course]] = [info["lecturer"]]
		else:
			data["lecturer_lecture"][course].append(info["lecturer"])

def load_courses(file_name):
	data = {}
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:
			course, lecturer, number_of_lectures, minimum_working_days, number_of_students = line
			data[course] = {"lecturer":lecturer, "number_of_lectures":int(number_of_lectures), "minimum_working_days":int(minimum_working_days), "number_of_students": int(number_of_students)}

	return data


def load_unavailability(file_name):
	data = {}
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:

			course, day, period = line

			if course in data:
				data[course]["day"].append(int(day))
				data[course]["period"].append(int(period))
			else:
				data[course] = {"day" : [int(day)], "period" : [int(period)]}
	return data


def load_rooms(file_name):
	data = {}
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:
			room, capacity = line
			data[int(room[1:])] = int(capacity)

	return data


def load_relations(file_name):
	data = {}
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:
			curriculum, course = line

			if curriculum in data:
				data[curriculum].append(course)
			else:
				data[curriculum] = [course]

	return data


def load_lecturers(file_name):
	data = []
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:
			data.append(line)

	return data


def load_curriculas(file_name):
	data = {}
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:
			curriculum, number_of_course = line
			data[curriculum] = int(number_of_course)

	return data


def load_basics(file_name):
	data = {}
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:
			courses, rooms, days, periods_per_day, curricula, constraints, lecturers = line
			data = {"courses": int(courses), "rooms": int(rooms) , "days": int(days),
			 		"periods_per_day" : int(periods_per_day),
					"curricula" : int(curricula), "constraints" : int(constraints),
					"lecturers" : int(lecturers)}

	return data
