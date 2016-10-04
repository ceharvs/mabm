__author__ = 'jgentile', 'ceharvey'

import mabm

class ElementDirectory:
    __dict = None

    def __init__(self):
        """Create a directory of elements"""
        self.__dict = {}

    def add_element(self, element):
        """Add an element to the directory,
        using the serialized element as the key
        """
        self.__dict[element.get_element_id().serialize()] = element

    def get_element(self, eid):
        """Return an element from the dictionary,
        using the serialized element_id or a string
        """
        if isinstance(eid, mabm.ElementID):
            return self.__dict[eid.serialize()]
        if isinstance(eid, str):
            return self.__dict[eid]

    def has_id(self, id):
        """Check to see if the dictionary contains an element_id"""
        return id in self.__dict

    def print_keys(self):
        """Error checking method to print out the element_id
        and the state of the element for all elements in the dictionary
        """
        print "printing element dict: key, state"
        for key, value in self.__dict.iteritems():
            print key, value.get_state()


