__author__ = 'jgentile', 'ceharvey'

import mabm
import numpy.random as npr


class Person(mabm.Agent):
    """
    Creates the person class which is a sub-class of Agent from the MABM module.

    A Person has:
        state: 0 or 1 depending on whether they have heard the rumor
        neighbors: list of assigned neighbors in initialization
    """

    __slots__ = ['__state', '__neighbors']

    def __init__(self, eid, state, model):

        mabm.Agent.__init__(self, model, None, eid)
        self.__state = state
        self.__neighbors = []

        #Adds an event (time step) to the model for every person added
        self.add_event(0)

    def add_event(self, time):
        """
        Add an event for the agent at a certain time.

        This event is added to the scheduler.
        """
        if self.__state == 0:
            self.get_model().add_event(time, self)

    def __str__(self):
        """
        Put the person into string form for simple review
        """
        return ""

    def serialize(self):
        """
        Serialize the person
        """
        return self.__state

    def add_neighbor(self, eid):
        """
        Add a neighbor to a person
        """
        self.__neighbors.append(eid)

    def get_neighbors(self):
        """
        Return the list of neighbors in a human readable form
        """
        return self.__neighbors

    def is_neighbor(self, eid):
        """
        Check if another person is in the list of neighbors
        """
        return eid in self.__neighbors

    def get_state(self):
        """
        Return the state of the person
        """
        return self.__state

    def update(self):
        """
        Update the person to determine if they have heard the rumor.  Calculation is based on
        proportion of neighbors that know the rumor.
        """

        # Number of neighbors
        neighbor_count = len(self.__neighbors)

        # Update iff state is 0 and the person has neighbors
        if self.__state == 0 and neighbor_count > 0:

            # Counter for neighbors that know the rumor
            neighbor_knows = 0
            model = self.get_model()

            eid = self.get_element_id()

            # Cycle through neighbors to gather state information
            for neighbor_eid in self.__neighbors:
                k = model.get_element(neighbor_eid).get_state()
                neighbor_knows += k

            # Compute the probability of hearing the rumor as the proportion of neighbors
            # that have heard the rumor.
            probability_of_hearing = neighbor_knows/float(neighbor_count)

            my_probability = npr.random()

            # Person hears the rumor!
            if my_probability <= probability_of_hearing:
                self.__state = 1
                # Send message to the model informing that the state has been changed,
                #  model checks to see if the element has an associated watch
                # ... if so broadcast at next sync time step
                model.element_state_change(eid)
                model.knowledge_total += 1

            # Person will repeat update process at the next timestep
            else:
                self.add_event(model.get_time()+1)

        return self.__state

    def get_element_requests(self):
        for i in self.__neighbors:
            self.get_model().request_element(i)
        return
