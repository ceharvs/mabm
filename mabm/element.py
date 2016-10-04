__author__ = 'jgentile', 'ceharvey'


import abc
import mabm


class Element(object):
    __metaclass__ = abc.ABCMeta
    # Slots functionality implemented to conserve memory
    __slots__ = ['__element_id']

    def __init__(self, eid):
        """Initialize an Element"""
        self.__element_id = eid

    @abc.abstractmethod
    def serialize(self):
        pass

    def get_element_requests(self):
        pass

    def set_element_id(self, eid):
        """Set an element_id and check if the id is valid"""
        if isinstance(eid, mabm.ElementID):
            self.__element_id = eid
        else:
            print 'Error in Agent.set_element_id(). Parameter is not mabm.ElementID'

    def get_element_id(self):
        """Return the element_id"""
        return self.__element_id
