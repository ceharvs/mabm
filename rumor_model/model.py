__author__ = 'jgentile', 'ceharvey'

import rumor_model
import mabm
import numpy.random as npr
from numpy import arange
import shutil
from mpi4py import MPI
import sys


class Model(mabm.Model):
    """
    Class defining the model for the basic Rumor Model Example.

    This example displays the spreading of knowledge of a rumor through a distributed
    population of agents.  An initial group of agents have knowledge of the model and
    spread this knowledge.  The probability of the rumor reaching an agent is proportional
    to the number of neighbors that have knowledge of the rumor.
    """
    __container = None

    def __init__(self, number_of_persons, zipf_param, p_knowledge, p_cross_processes, write_file=False,
                 notify=False, requests=False):
        """
        Initialize the Rumor Model.

        Parameters:
            number_of_persons: number of agents per processor
            zipf_param: parameter that determines number of neighbors per person. (NOT IN USE)
            p_knowledge: probability that an agent knows the rumor at the initalization
                of the model
            p_cross_processes: probability of an "neighbor" agent being located on a foreign
                processor
            write_file: write agent state and connection output to a file
            notify: print notifications about the number of steps completed
            requests: use the requests method for communication
        """

        # Call the MABM module to initiate the model
        self.initialize_model(not requests)

        # Create the container for persons
        self.__container = rumor_model.PersonList()

        # Create the element ID dictionary
        eid_gen_dict = {0: [rumor_model.Person, rumor_model.PersonForm]}
        self.set_element_id_generator(eid_gen_dict)

        # Compile a list of processes and of other processes
        self.other_processes = range(self.get_world_size())
        self.other_processes.remove(self.get_rank())

        # Define the input parameters
        self.pxp = p_cross_processes
        self.notify = notify
        self.p_knowledge = p_knowledge
        self.watches = not requests
        self.number_of_persons = number_of_persons
        self.write_file = write_file
        self.knowledge_total = 0

    def create_agent(self, my_id):
        """
        Function to create a single agent in the model
        """

        # Generate the eid of this agent
        eid = self.get_new_element_id(rumor_model.Person)

        # Generate a random probability which determines rumor knowledge
        if npr.random() < self.p_knowledge:
            knowledge = 1
            self.knowledge_total += 1
        else:
            knowledge = 0

        # Create the person and randomly select a number of neighbors
        p = rumor_model.Person(eid, knowledge, self)
        # TODO: Implement social networks
        num_of_neighbors = 2

        # Error checking to make sure no one has more neighbors than people available
        possible_neighbors = self.number_of_persons*self.get_world_size() - 1
        if num_of_neighbors > possible_neighbors:
            num_of_neighbors = possible_neighbors

        # Create empty trackers for the neighbors to be added to the agent
        my_neighbor_list = set()
        neighbors_list = ""

        # If pxp < 0, all agents in system have equal probability of becoming a neighbor.
        if self.pxp < 0:
            # Compute the agent's number: rank * persons_per_processor + id
            me = self.get_rank()*self.number_of_persons + my_id

            # While the length of my_neighbor_list < the number of neighbord desired, continue to
            # add neighbors to the list.
            while len(my_neighbor_list) < num_of_neighbors:
                # Generate a random number from all possible neighbors
                new_neighbor = npr.randint(possible_neighbors)

                # If this new number is >= the me number, increment by 1 to avoid choosing
                # oneself as the neighbor
                if new_neighbor >= me:
                    new_neighbor += 1

                # Compute the neighbor number by finding the id on the processor
                neighbor_number = new_neighbor % self.number_of_persons

                # Compute the processor by dividing by the number of persons
                # Integer division helps to compute this number
                neighbor_process = new_neighbor / self.number_of_persons

                # Generate the element_id of the new neighbor
                new_neighbor_eid = mabm.ElementID(0, neighbor_number, neighbor_process)

                # If the neighbor is on a foreign processor, add watches or requests as necessary
                if neighbor_process != self.get_rank():
                    if self.watches:
                        # Add element watch to the neighbor
                        self.request_element_watch(new_neighbor_eid)
                        self.add_watching(new_neighbor_eid)
                    else:
                        # Requests Version
                        self.request_element(new_neighbor_eid)
                # Add the neighbor to the list
                my_neighbor_list.add(new_neighbor_eid)

        # For simulations with a specific pxp assigned
        else:
            # While the length of my_neighbor_list < the number of neighbord desired, continue to
            # add neighbors to the list.
            while len(my_neighbor_list) < num_of_neighbors:
                # Determine if the neighbor will be on a foreign process
                if npr.random() <= self.pxp:
                    # Create a neighbor on a foreign process

                    # Select a processor from the available other processors
                    value = npr.randint(0, self.get_world_size()-1)
                    neighbor_process = self.other_processes[value]
                    # Randomly generate the birth order of the neighbor
                    neighbor_number = npr.randint(0, self.number_of_persons)
                    foreign_neighbor = True
                else:
                    # Neighbor is local
                    neighbor_process = self.get_rank()

                    # Randomly pick a birth order number for the new neighbor
                    neighbor_number = npr.randint(0, self.number_of_persons - 1)
                    foreign_neighbor = False

                    # Error-checking code so you can't pick yourself as a neighbor
                    if neighbor_number >= my_id:
                        neighbor_number += 1

                # Compute the eid of the new neighbor
                new_neighbor_eid = mabm.ElementID(0, neighbor_number, neighbor_process)

                # If the neighbor is on a foreign process, add appropriate requests or watches
                if foreign_neighbor:
                    if self.watches:
                        # Add element watch to the neighbor
                        self.request_element_watch(new_neighbor_eid)
                        self.add_watching(new_neighbor_eid)
                    else:
                        # Requests Version
                        self.request_element(new_neighbor_eid)
                # Add the neighbor to the lis
                my_neighbor_list.add(new_neighbor_eid)

        # Add neighbors from list to person's neighbors
        for neighbor in my_neighbor_list:
            p.add_neighbor(neighbor)
            if self.write_file:
                neighbors_list += str(eid) + ';' + neighbor + '\n'

        # Write information out to the file
        if self.write_file:
            self.neighbors_file.write(neighbors_list)
            self.agents_file.write(str(eid)+','+str(eid)+','+str(self.get_rank())+','+str(knowledge)+'\n')

        # Add element to directory and the container.
        self.add_element_to_directory(p)
        self.__container.add_element(p)

    def build_agents(self, notify, pxp, p_knowledge):
        """
        Function to build the agents needed for the simulation
        """

        # File setup if write command is turned on
        if self.write_file:
            filename = 'node_network'+str(self.get_rank())+'.csv'
            self.neighbors_file = open(filename,'w')
            filename = 'node_agents'+str(self.get_rank())+'.csv'
            self.agents_file = open(filename,'w')
            if self.get_rank() == 0:
                self.agents_file.write('ID, Label, Process, Knows_Rumor_Init\n')
                self.neighbors_file.write('Source;Target\n')

        # Create each agent that is needed per processor
        for i in arange(0, self.number_of_persons):
            self.create_agent(i)

        # File close and clean-up
        if self.write_file:
            self.neighbors_file.close()
            self.agents_file.close()

        # Reduce the calculations from all processors to a single number
        KNOWLEDGE_TOTAL = self.__mabm_comm.reduce(self.knowledge_total, MPI.SUM, root=0)
        POPULATION = self.number_of_persons*self.get_world_size()
        if self.get_rank() == 0:
            saturation = KNOWLEDGE_TOTAL/float(POPULATION)
            print "Initial Saturation: \t %d/%d \t = %0.4f" %\
                  (KNOWLEDGE_TOTAL, POPULATION, saturation)
    
    def post_update_model(self):
        """
        Update the model and report the current saturation rate of the rumor on this process.
        """
        if self.write_file:
            self.knowledge_total = 0
            filename_old = 'node_agents'+str(self.get_rank())+'.csv'
            original_agents_file = open(filename_old, 'r')
            filename_new = 'final_agents'+str(self.get_rank())+'.csv'
            agents_new_file = open(filename_new, 'w')
            if self.get_rank() == 0:
                line = next(original_agents_file)
                agents_new_file.write(line.rstrip()+', Knows_Rumor_'+str(self.__mabm_time)+'\n')

            i = 0
            for line in original_agents_file:
                eid = mabm.ElementID(0, i, self.get_rank())
                knowledge = self.__container.send_element_state(eid)
                agents_new_file.write(line.rstrip()+','+str(knowledge)+'\n')
                self.knowledge_total += knowledge
                i += 1

            agents_new_file.close()
            original_agents_file.close()
            shutil.move(filename_new, filename_old)

        # Reduce the calculations from all processors to a single number
        # Reduce the calculation to a single point
        KNOWLEDGE_TOTAL = self.__mabm_comm.reduce(self.knowledge_total, MPI.SUM, root=0)
        POPULATION = self.number_of_persons*self.get_world_size()
        if self.get_rank() == 0:
            saturation = KNOWLEDGE_TOTAL/float(POPULATION)
            print "Time %d Saturation: \t %d/%d \t = %0.4f"%(self.__mabm_time, KNOWLEDGE_TOTAL, POPULATION, saturation)
