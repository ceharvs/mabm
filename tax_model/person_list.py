__author__ = 'jgentile', 'ceharvey'

import mabm

class PersonList(mabm.Container):
    """
    Container of people for the model
    """
    __dict = None

    def __init__(self):
        """
        Initialize an empty dictionary as a container.
        """
        self.__dict = {}

    def add_element(self,element):
        """
        Add an element to the container
        """
        self.__dict[element.get_element_id().serialize()] = element

    def remove_element(self,eid):
        """
        Remove an element from the container
        """
        del self.__dict[eid]

    def send_element_state(self, eid):
        """
        Return the state of an element
        """
        return self.__dict[eid.serialize()].get_state()

    def update(self):
        """
        Update each element in the dictionary
        """
        for key in self.__dict:
            self.__dict[key].update()

    def get_element_requests(self):
        """
        Get the requests for each element
        """
        for key in self.__dict:
            self.__dict[key].get_element_requests()


