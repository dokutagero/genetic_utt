import csv
path = "UniversityTimetablingCompetition/Test01/"

def load(params):
	data = {}
	data["basics"] = (load_basics(params[0]))
	data["courses"] = (load_courses(params[1]))
	data["lecturers"] = (load_lecturers(params[2]))
	data["rooms"] = (load_rooms(params[3]))
	data["curricula"] = (load_curriculas(params[4]))
	data["relations"] = (load_relations(params[5]))
	data["unavailability"] = (load_unavailability(params[6]))

	return data

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
			data[course] = {"day": day, "period": period}

	return data


def load_rooms(file_name):
	data = {}
	with open(path+file_name, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=' ')
		csv_reader.next()
		for line in csv_reader:
			room, capacity = line
			data[room] = {"capacity": capacity}

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
			data[curriculum] = number_of_course

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
