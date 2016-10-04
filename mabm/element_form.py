__author__ = 'jgentile', 'ceharvey'

import mabm
import abc

class ElementForm:
    __metaclass__ = abc.ABCMeta
    # Using slots functionality to conserve memory
    __slots__ = ['__element_id']

    def __init__(self, eid):
        """Create an Element form or shadow/ghost copy of the element"""
        if isinstance(eid, mabm.ElementID):
            self.__element_id = eid
        else:
            print 'Error in Agent.set_element_id(). Parameter is not mabm.ElementID'

    @abc.abstractmethod
    def update(self):
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