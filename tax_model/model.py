__author__ = 'ceharvey', 'smichel'

import tax_model
import mabm
import numpy.random as npr
from numpy import arange
import shutil
from mpi4py import MPI
import sys
import linecache
import time


class Model(mabm.Model):
    """
    Class defining the model for the basic Taxpayer Model for the tax chapter.

    SM-TODO: or ask Matt for a description here.
    """
    __container = None

    def __init__(self, total_taxpayers, time_steps, tax_rate, penalty_rate, audit_prob, app_rate, max_audit, apprehension,
                 network_file, prop_honest, prop_dishonest, identifier, write_file=False, notify=False):
        """
        :param taxpayers:   number of agents per processor
        :param time_steps:  The number of discrete steps of time (also called "ticks") that occur in a single run of
                            the model. Each time step consists of each agent activating, surveying its network, and
                            making a decision based on its defining parameters.
        :param tax_rate:    The income tax rate, or percent of total income that will be collected after each time
                            step.  This model assumes a flat tax, irrespective of an agent's current income or wealth.
                            This tax rate becomes important in the agent's decision making heuristic, whether or not
                            the agent will evade taxes.

        :param penalty_rate:
        :param audit_prob:  The objective probability that any agent that is evading taxes will be audited in any
                            given time step.
        :param app_rate:    Same as audit probability.
        :param max_audit:   If apprehension is True, this is the number of timesteps an imitator agent will act
                            honestly immediately after being audited.
        :param apprehension: A Boolean variable, indicating whether an agent has been apprehended for tax evasion
                            (True) or not (False).
        :param network_file: File to read in the network structure.
        :param prop_honest: Proportion of agents that are completely honest taxpayers and will never attempt to evade
                            taxes.
        :param prop_dishonest: Proportion of agents that are utility maximizers who, given their bounded rational
                            belief that they will be audited and their individual level of risk aversion, will attempt
                            to evade paying taxes as much as possible.
        :param write_file:  write agent state and connection output to a file
        :param notify:      print notifications about the number of steps completed
        :return:
        """

        # Initialize a start time for the model
        self.__start_time = time.time()

        # Call the MABM module to initiate the model
        self.initialize_model(True)

        # Create the container for persons
        self.__container = tax_model.PersonList()

        # Create the element ID dictionary
        eid_gen_dict = {0: [tax_model.Person, tax_model.PersonForm]}
        self.set_element_id_generator(eid_gen_dict)

        # Compile a list of processes and of other processes
        self.other_processes = range(self.get_world_size())
        self.other_processes.remove(self.get_rank())

        # Check taxpayers to make sure this number is divisible by the number of processors
        if total_taxpayers % self.get_world_size() != 0:
            if self.get_rank() == 0:
                exit("Number of taxpayers not divisible by the number of processors!")
            else:
                exit()

        # Define the input parameters
        self.taxpayers = total_taxpayers / self.get_world_size()
        self.time_steps = time_steps
        self.tax_rate = tax_rate
        self.penalty_rate = penalty_rate
        self.audit_prob = audit_prob
        self.app_rate = app_rate
        self.max_audit = max_audit
        self.apprehension = apprehension
        self.prop_honest = prop_honest
        self.prop_dishonest = prop_dishonest

        self.network_file = network_file
        self.notify = notify
        self.write_file = write_file

        self.vmtr = 0
        self.vmtr_list = []
        self.temp_storage = identifier + '_np-' + str(self.get_world_size())

    def create_agent(self, my_id):
        """
        Function to create a single agent in the model
        """

        # Generate the eid of this agent
        eid = self.get_new_element_id(tax_model.Person)

        # Assign Personal Attributes

        # Set the personality
        personality_random = npr.uniform()
        if personality_random < self.prop_honest:
          personality = "Honest"
        elif personality_random < self.prop_honest + self.prop_dishonest:
          personality = "Dishonest"
        else:
          personality = "Imitator"
        actual_income = 100.0
        ps_value = npr.uniform(0, 1)
        # This can not be 0.0, no dividing by 0
        risk_aversion = npr.uniform(0, 1)

        # Create the person and randomly select a number of neighbors
        p = tax_model.Person(eid, personality, actual_income, ps_value, risk_aversion, self)

        ##################################
        # Add neighbors to the agent
        ##################################

        # Create empty trackers for the neighbors to be added to the agent
        my_neighbor_list = set()
        neighbors_list = ""

        me = self.get_rank()*self.taxpayers + my_id

        neighbors_from_file = linecache.getline(self.network_file, me+1).strip().split(",")
        #print neighbors_from_file
        #neighbors_from_file = [n for (n, e) in enumerate(neighbors_from_file) if e == '1']
        # Add neighbors to the agent's system
        for new_neighbor in neighbors_from_file:
            # Skip blank lines
            if new_neighbor == '':
                break

            # Convert to integer
            new_neighbor = int(new_neighbor)

            # Compute the neighbor number by finding the id on the processor
            neighbor_number = new_neighbor % self.taxpayers

            # Compute the processor by dividing by the number of persons
            # Integer division helps to compute this number
            neighbor_process = new_neighbor / self.taxpayers

            # Generate the element_id of the new neighbor
            new_neighbor_eid = mabm.ElementID(0, neighbor_number, neighbor_process)

            # If the neighbor is on a foreign processor, add watches or requests as necessary
            if neighbor_process != self.get_rank():
                # Add element watch to the neighbor
                self.request_element_watch(new_neighbor_eid)
                self.add_watching(new_neighbor_eid)

            # Add the neighbor to the list
            my_neighbor_list.add(new_neighbor_eid)

        # Add neighbors from list to person's neighbors
        for neighbor in my_neighbor_list:
            p.add_neighbor(neighbor)

        # Write information out to the file
        if self.write_file:
            self.agents_file.write(str(eid) + ',' + str(eid) + ',' + str(self.get_rank()) + ',' + str(personality) +
                                   ',0,' + str(actual_income) + ',' + str(ps_value) + ',' + str(risk_aversion)  + '\n')

        # Add element to directory and the container.
        self.add_element_to_directory(p)
        self.__container.add_element(p)

    def build_agents(self):
        """
        Function to build the agents needed for the simulation
        """

        # File setup if write command is turned on
        if self.write_file:
            filename = self.temp_storage + '_node_agents'+str(self.get_rank())+'.csv'
            self.agents_file = open(filename, 'w')
            if self.get_rank() == 0:
                self.agents_file.write('ID, Label, Process, Personality, Declared_Income, Actual_Income, '
                                       'ps_value, Risk_Aversion\n')

        # Create each agent that is needed per processor
        for i in arange(0, self.taxpayers):
            self.create_agent(i)

        # File close and clean-up
        if self.write_file:
            self.agents_file.close()

        # TODO: Rethink general outputs
        # Reduce the calculations from all processors to a single number
        TOTAL_VMTR = self.__mabm_comm.reduce(self.vmtr, MPI.SUM, root=0)
        if self.get_rank() == 0:
            print "Initial VMTR: \t %0.4f" % (TOTAL_VMTR)

    def run(self):
        """
        Run the model by completing the update method for a specified number
        of time steps.  Override the MABM run module
        """
        while self.__mabm_time < self.time_steps:
            self.update()

        return self.vmtr_list
    
    def post_update_model(self):
        """
        Update the model and report the current saturation rate of the rumor on this process.
        """

        # Keep out for now until we figure out what we want to report.
        if self.write_file:
            self.vmtr = 0
            filename_old = self.temp_storage + '_node_agents'+str(self.get_rank())+'.csv'
            original_agents_file = open(filename_old, 'r')
            filename_new = self.temp_storage + '_final_agents'+str(self.get_rank())+'.csv'
            agents_new_file = open(filename_new, 'w')
            if self.get_rank() == 0:
                line = next(original_agents_file)
                agents_new_file.write(line.rstrip()+', Declared_Over_Actual_'+str(self.__mabm_time)+'\n')

            i = 0
            for line in original_agents_file:
                eid = mabm.ElementID(0, i, self.get_rank())
                declared_over_actual = self.__container.send_element_state(eid)
                agents_new_file.write(line.rstrip()+','+str(declared_over_actual)+'\n')
                try:
                    self.vmtr += declared_over_actual
                except TypeError:
                    # Exception to account for None Types in declared_over_actual
                    self.vmtr += 0
                i += 1
            agents_new_file.close()
            original_agents_file.close()
            shutil.move(filename_new, filename_old)

        # Reduce the calculations from all processors to a single number
        # Reduce the calculation to a single point
        TOTAL_VMTR = self.__mabm_comm.reduce(self.vmtr, MPI.SUM, root=0)
        POPULATION = self.taxpayers*self.get_world_size()
        if self.get_rank() == 0:
            mean_vmtr = TOTAL_VMTR/float(POPULATION)
            print "Time %d VMTR: \t = %0.4f" % (self.__mabm_time, mean_vmtr)
            self.vmtr_list.append(mean_vmtr)
