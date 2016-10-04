__author__ = 'jgentile', 'ceharvey'

import rumor_model
import mabm

class PersonForm(mabm.ElementForm):
    """
    Creates the person form class which is a sub-class of ElementForm from the MABM module.

    A PersonForm has:
        state: 0 or 1 depending on whether they have heard the rumor
    """
    __slots__ = ['__state']

    def __init__(self, eid, state):
        """
        Create a ghost or shadow copy of the Person.
        """
        mabm.ElementForm.__init__(self, eid)
        self.__state = state

    def update(self, state):
        """
        Perform an update of state for the PersonForm
        """
        self.__state = state

    def get_state(self):
        """
        Return the state of the PersonForm
        """
        return self.__state

    def get_eid(self):
        """
        Return the eid of the PersonForm
        """
        return self.__eid