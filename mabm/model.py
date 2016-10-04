__mabm_author__mabm_ = 'jgentile', 'ceharvey'

import mabm
from mpi4py import MPI
import abc
import numpy.random as npr

class Model:
    __metaclass__ = abc.ABCMeta

    __mabm_element_directory = {}
    __mabm_rank = None
    __mabm_world_size = None
    __mabm_comm = None

    __mabm_element_requests = None
    __mabm_element_watches = None
    __mabm_watching = None
    __mabm_element_changed_and_watched = None
    __mabm_element_id_generator = None
    __mabm_element_forms = None
    __mabm_new_connections = None

    __mabm_scheduler = None

    __mabm_time = 0
    __mabm_next_time = None

    def initialize_model(self, watches):
        """
        This method should be called during the instantiation of a concrete mabm.Model
        as it sets up the Scheduler and structures used for process communication and
        element synchronization.
        """

        # Specify the model to use watches or requests only
        self.__watches = watches

        # Initialize MPI communicator, get rank and world size.
        self.__mabm_comm = MPI.COMM_WORLD
        self.__mabm_rank = self.__mabm_comm.Get_rank()
        self.__mabm_world_size = self.__mabm_comm.Get_size()

        # Instantiate the structures used for element synchronization
        self.__mabm_element_requests = {}
        # Set of elements that are being watched
        self.__mabm_element_watches = set()     # Mutual Watching
        # Set of elements that the processor is watching
        self.__mabm_watching = set()            # One way watching
        self.__mabm_element_changed_and_watched = set()
        self.__mabm_element_directory = mabm.ElementDirectory()
        self.__mabm_element_forms = {}
        # List of new connections that cross processors
        self.__mabm_new_connections = []

        # Initialize the scheduler
        self.__mabm_scheduler = mabm.Scheduler()

    def add_element_to_directory(self, element):
        """
        Adds an element to the model's directory. This should be called each time an agent
        is created or moves on to this process.

        A directory is maintained for the location of all Elements and ElementForms on a
        process. This eases locating the agent by ElementID.
        """
        self.__mabm_element_directory.add_element(element)

    def update_model(self):
        """
        This method is called before element updates are called from the scheduler. The stub
        in mabm.Model is meant to be overridden if a model implementation demands this functionality.
        """
        pass

    def post_update_model(self):
        """
        This method is called after element updates are finished. It is meant to be overridden
        if a model implementation demands this functionality.
        """
        pass

    def add_watching(self, eid):
        """
        Add an element (using the eid) to the set of elements that the processor is watching.

        Processor watches these elements which are located on a FOREIGN processor.
        """
        if isinstance(eid, str):
            self.__mabm_watching.add(eid)
        else:
            self.__mabm_watching.add(eid.serialize())

    def add_watch(self, eid):
        """
        Requests a watch on an element give an element_id (eid). A watched-element's status
        will be synchronized each time its state changes.

        This is the list of a processor's OWN elements that are being watched.
        """
        if isinstance(eid, str):
            self.__mabm_element_watches.add(eid)
        else:
            self.__mabm_element_watches.add(eid.serialize())

    def remove_watch(self, eid):
        """
        Removes a watch on an element.

        This is only for the processor's OWN elements.
        """
        if isinstance(eid, str):
            self.__mabm_element_watches.discard(eid)
        else:
            self.__mabm_element_watches.discard(eid.serialize())

    def element_is_watched(self,eid):
        """
        Returns True if an element has at least one watch, False otherwise.

        This is determined by checking if the element is in the processor's OWN
        list of watched elements.
        """
        if isinstance(eid, str):
            if eid in self.__mabm_element_watches:# or eid in self.__mabm_mutual_watch:
                return True
            else:
                return False

        if isinstance(eid, mabm.ElementID):
            if eid.serialize() in self.__mabm_element_watches:# or eid.serialize() in self.__mabm_mutual_watch:
                return True
            else:
                return False

    def element_state_change(self, eid):
        """
        If an element is being watched, add this element to the list of changed
        and watched elements.

        This method is only called when an element has experienced a change in state.
        """
        # Check if being watched
        if self.element_is_watched(eid):
            # Add to structure to notify element has been change
            self.__mabm_element_changed_and_watched.add(eid.serialize())

    def request_element(self, eid):
        """
        Adds an element request to the model so it can be synchronized during the current update().
        The eid should be an ElementID (non-serialized).
        """
        # Check if the element is on the current processor
        if not eid.get_process() == self.__mabm_rank:
            serialized = eid.serialize()
            # If the element is not in the list of element requests, then add the element.
            if not serialized in self.__mabm_element_requests:
                self.__mabm_element_requests[serialized] = 0

    def add_foreign_network_connection(self, original_eid, connection_eid):
        """
        Add a network connection between elements on foreign procssors.

        Append this information to the list of new connections.
        """
        self.__mabm_new_connections.append([connection_eid, original_eid])

    def synchronize_social_networks(self):
        """
        This function should be called after the initialization of the agents and
        can be additionally called at the beginning of every time step if the agents connections and
        network change and develop over the course of the simulation.

        This method synchronizes the networks between the different processors.  When there is
        a connection between agents on separate processors, the add_foreign_network_connection() method
        is called to add the connection to the list.  This method synchronized those lists and has each
        of the processors add the requested connections.
        """

        all_connections = None

        # Root node populates a list of all connections and fills it with own connections
        if self.__mabm_rank == 0:
            all_connections = list(self.__mabm_new_connections)

            # Receive information from all other processors
            for i in range(1, self.__mabm_world_size):
                connections = self.__mabm_comm.recv(source=i, tag=1)
                # Append connection from other processors to the all_connections list
                all_connections += connections
        else:
            self.__mabm_comm.send(self.__mabm_new_connections, dest=0, tag=1)

        # Broadcast the list of all_connections to all processors
        all_connections = self.__mabm_comm.bcast(all_connections, root=0)

        # Cycle through all of the connections to pull out element
        for connection in all_connections:
            # Check if the connection processor is the current processor
            # connection[0] is the element doing the watching
            if int(str(connection[0]).split('|')[2]) == self.__mabm_rank:
                # Get the element from the directory
                element = self.__mabm_element_directory.get_element(str(connection[0]))

                # Add neighbor to the agent's network
                element.add_to_network(connection[1])

                # Request that the connection node be added to the watched list.
                self.request_element_watch(connection[1])

    def request_element_watch(self, eid):
        """
        This requests an element watch given an Element ID. If an element is watched, its state is synchronized across
        processes. Note that the element update function should contain the model.element_state_change(eid) method.
        """
        if isinstance(eid, str):
            self.__mabm_element_requests[eid] = 1
        if isinstance(eid, mabm.ElementID):
            self.__mabm_element_requests[eid.serialize()] = 1

    def resolve_element_request(self):
        """
        resolve_element_requests() is called during a simulation timestep. The root element aggregates the pending
        element requests in one structure (all_requests). This structure is broadcast and all processes generate an
        object of information for all requested elements local to it (requested_element_information).

        The root process aggregates all element information from the processes and broadcasts the structure
        (requested_element_information).

        Finally, processes receive information for their requested elements and generate or update element forms.
        """

        all_requests = None

        # Root node populates list of all requests, fill it with own requests
        if self.__mabm_rank == 0:
            all_requests = self.__mabm_element_requests.copy()
            # Receive information from all other processors
            for i in range(1, self.__mabm_world_size):
                request = self.__mabm_comm.recv(source=i, tag=1)
                for eid in request:
                    if not eid in all_requests:
                        all_requests[eid] = 0
                    if request[eid] == 1:  # if this is a watch
                        all_requests[eid] = 1
        else:
            self.__mabm_comm.send(self.__mabm_element_requests, dest=0, tag=1)

        all_requests = self.__mabm_comm.bcast(all_requests, root=0)

        my_requests = {}

        for eid in all_requests:
            if int(eid.split('|')[2]) == self.__mabm_rank:
                element = self.__mabm_element_directory.get_element(eid)
                # If the element is on this process, serialize it
                my_requests[eid] = element.serialize()
                if all_requests[eid] == 1:
                    self.add_watch(eid)
                #if all_requests[eid] == 2:
                #    self.add_mutual_watch(eid)

        # My requests only contains requested agent states, does not yet contain
        # the watched elements whose state has changed

        # Adds in the changed and watched elements
        for eid in self.__mabm_element_changed_and_watched:
            element = self.__mabm_element_directory.get_element(eid)
            my_requests[eid] = element.serialize()

        requested_element_information = {}

        # Root node makes a master list
        if self.__mabm_rank == 0:
            requested_element_information = my_requests.copy()
            for i in range(1, self.__mabm_world_size):
                element_info = self.__mabm_comm.recv(source=i, tag=2)
                for eid in element_info:
                    requested_element_information[eid] = element_info[eid]
        else:
            self.__mabm_comm.send(my_requests, dest=0, tag=2)

        # Broadcast master list of requested agent states
        requested_element_information = self.__mabm_comm.bcast(requested_element_information, root=0)

        # Resolve element requests by getting the state of the element if in the list or
        # add the element and it's state to the list if not already available.
        for element in requested_element_information:
            requested_id = str(element)

            if requested_id in self.__mabm_watching or element in self.__mabm_element_requests:
                e = mabm.ElementID(requested_id)
                state = requested_element_information[element]
                if self.__mabm_element_directory.has_id(requested_id):
                    self.__mabm_element_directory.get_element(requested_id).update(state)
                # Create a new, local copy of the element
                else:
                    form_constructor = self.__mabm_element_id_generator.get_form_from_type(e.get_type())
                    form = form_constructor(e, requested_element_information[requested_id])
                    #form.set_element_id(e)
                    #form.update(requested_element_information[requested_id])
                    self.__mabm_element_directory.add_element(form)
                    self.__mabm_element_forms[requested_id] = form

        self.__mabm_element_requests = {}
        self.__mabm_element_changed_and_watched = set()

    def get_next_timestep(self):
        """
        Returns the next event's time.

        This is done by checking the scheduler for the next time event in the list of
        scheduled events.
        """
        next_timestep = self.__mabm_scheduler.get_next_event_time()
        if self.__mabm_rank == 0:
            for i in range(1, self.get_world_size()):
                t = self.__mabm_comm.recv(source=i, tag=3)
                if t < next_timestep:
                    next_timestep = t
        else:
            self.__mabm_comm.send(next_timestep, dest=0, tag=3)
        self.__mabm_next_time = self.__mabm_comm.bcast(next_timestep, root=0)
        return self.__mabm_next_time

    def update(self):
        """
        Update the model for a time step.

        1. Update the time to mabm_next_time
        2. If Requests Version: Get element requests
        3. Resolve element requests
        4. Update the scheduler
        5. Get the next time step
        6. Complete post_update_model()
        """
        if self.__mabm_next_time:
            self.__mabm_time = self.__mabm_next_time

        if not self.__watches:
            self.__mabm_scheduler.get_element_requests(self.__mabm_time)
        self.resolve_element_request()
        self.__mabm_scheduler.update(self.__mabm_time)
        self.get_next_timestep()
        self.post_update_model()

    def run(self):
        """
        Run the model by completing the update method for a specified number
        of time steps.
        """
        while self.__mabm_time != sys.maxint:
            self.update()

    def set_element_id_generator(self,dict):
        """
        This method configures the structure which provides unique ElementIDs for the simulation.
        """
        self.__mabm_element_id_generator = mabm.ElementIDGenerator(self.__mabm_rank, dict)

    def get_new_element_id(self,type):
        """
        Gets a new, unique ElementID for the specified element type.
        """
        return self.__mabm_element_id_generator.get_new_element_id(type)

    def add_event(self, time, element):
        """
        Adds as event to the scheduler. Events are given a time and pointer to the Element. Simulation time moves forward
        from early to later events. Element.update() is called for each attached event.
        """
        self.__mabm_scheduler.add_event(time, element)

    def get_time(self):
        """
        Gets the current simulation time
        """
        return self.__mabm_time

    def set_time(self):
        """
        Sets the current simulation time
        """
        return self.__mabm_time

    def get_rank(self):
        """
        Returns the process's rank in the MPI world
        """
        return self.__mabm_rank

    def get_world_size(self):
        """
        Returns the MPI world size (the number of processes+1)
        """

        return self.__mabm_world_size

    def get_element(self,eid):
        return self.__mabm_element_directory.get_element(eid)
