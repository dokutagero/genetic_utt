from FitnessFunctionBase import FitnessFunctionBase


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
        """
        pass

    def check_room_occupancy_constraint(self):
        """
        Two lectures cannot take place in the same room in the same time slot.
        """
        pass

    def check_conflicts_constraint(self):
        """
        Lectures of courses in the same curriculum or taught by the same
        lecturer must all be scheduled in different time slots.
        """
        pass

    def check_availability_constraint(self):
        """
        Some courses cannot be scheduled at specific time slots.
        """
        pass
