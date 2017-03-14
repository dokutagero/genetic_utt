from abc import ABCMeta, abstractmethod

class FitnessFunctionBase(object):

    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.data = data
        pass

    @abstractmethod
    def evaluate(self, individual):
        pass
