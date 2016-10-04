__author__ = 'jgentile', 'ceharvey'

import rumor_model
import mabm

class PersonForm(mabm.ElementForm):
    """
    Creates the person form class which is a sub-class of ElementForm from the MABM module.

    A PersonForm has:
        declared_over_actual: persons declared income divided by the actual
    """
    #__slots__ = ['__state']

    def __init__(self, eid, declared_over_actual):
        """
        Create a ghost or shadow copy of the Person.
        """
        mabm.ElementForm.__init__(self, eid)
        self.__declared_over_actual = declared_over_actual

    def update(self, declared_over_actual):
        """
        Perform an update of state for the PersonForm
        """
        self.__declared_over_actual = declared_over_actual

    def get_state(self):
        """
        Return the state of the PersonForm
        """
        return self.__declared_over_actual

    def get_eid(self):
        """
        Return the eid of the PersonForm
        """
        return self.__eid