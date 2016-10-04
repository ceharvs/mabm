__author__ = 'jgentile', 'ceharvey'

import abc
import mabm

class Agent(mabm.Element):
    __metalass__ = abc.ABCMeta
    # Slots functionality implemented to conserve memory
    __slots__ = ['__model', '__container']

    def __init__(self, model, container, eid):
        """Initialize an agent as an object of the Element class"""
        mabm.Element.__init__(self, eid)
        self.__model = model
        self.__container = container

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def get_element_requests(self):
        pass

    def set_model(self, model):
        self.__model = model

    def get_model(self):
        return self.__model

    def set_container(self, container):
        self.__container = container

