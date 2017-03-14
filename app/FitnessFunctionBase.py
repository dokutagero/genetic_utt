from abc import ABCMeta, abstractmethod

class FitnessFunctionBase(object):

    """Parent class for dealing with fitness functions and constraint checkers.


    Attributes:
        data {dict}: Single dictionary containing the data used in a particular
                        problem..

    """

    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.data = data
        pass

    @abstractmethod
    def evaluate(self, individual):
        pass
