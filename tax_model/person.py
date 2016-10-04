__author__ = 'jgentile', 'ceharvey', 'smichel'

import mabm
import numpy.random as npr
import numpy as np
import random
import time

class Person(mabm.Agent):
    """
    Creates the person class which is a sub-class of Agent from the MABM module.

    A Person has:
        eid: element Id
        state: String describing personality type: honest, dishonest, imitator
        declared_income: declared income of the agent
        actual_income: actual income of the agent
        ps_value: probability of an audit
        risk_aversion: personal risk aversion
        audit_count: number of audit's the person has experienced
        lower_bound: lower bound of the income the person will declare
        declared_over_actual: declared / actual
        neighbors: list of assigned neighbors in initialization
    """

    def __init__(self, eid, personality, actual_income,
                 ps_value, risk_aversion, model):

        mabm.Agent.__init__(self, model, None, eid)
        self.__state = personality
        self.__declared_income = None
        self.__actual_income = actual_income
        self.__ps_value = ps_value
        self.__risk_aversion = risk_aversion

        self.__audit_count = 0
        self.__apprehended = False
        self.__neighbors = []
        self.__declared_over_actual = None
        self.__lower_bound = None
        
        # Adds an event (time step) to the model for every person added
        self.add_event(0)

    def add_event(self, time):
        """
        Add an event for the agent at a certain time.

        This event is added to the scheduler.
        """
        self.get_model().add_event(time, self)

    def __str__(self):
        """
        Put the person into string form for simple review
        """
        return self.get_element_id()

    def serialize(self):
        """
        Serialize the person
        """
        return self.get_declared_over_actual()

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
        Method to return the state of an element.  Must be included.
        :state:
        """
        return self.get_declared_over_actual()

    def get_declared_over_actual(self):
        """
        Return the state of the person
        """
        if self.__declared_income:
            self.__declared_over_actual = self.__declared_income / self.__actual_income
            return self.__declared_over_actual
        else:
            return None

    def update_declared_income(self):
        """
        Update the person's declared income in the model.
        The person will declare their income differently depending if they are honest, dishonest, or imitators.
        """

        # Get the model to access the global variables
        model = self.get_model()
        # Imitator agents always care about their neighbors' behaviors, if neighbors exist; otherwise, behave as Honest
        if self.__state == "Imitator":
            # Declares a proportion of income based on neighbors' behaviors
            # Number of neighbors -- only Imitator agents care about neighbors
            neighbor_count = len(self.__neighbors)

            if neighbor_count > 0:
                # Counter for neighbors that know the rumor
                sum_declared_over_actual = 0

                # Cycle through neighbors to gather state information
                for neighbor_eid in self.__neighbors:
                    k = model.get_element(neighbor_eid).get_state()
                    if k:
                        sum_declared_over_actual += k

                # Compute the declared income
                self.__declared_income = (1.0 / neighbor_count) * sum_declared_over_actual * self.__actual_income
            
            else:
                self.__declared_income = self.__actual_income

        # Honest agents always declare actual income completely
        elif self.__state == "Honest":
            self.__declared_income = self.__actual_income

        # Dishonest agents declare:
        # 1) no income ONLY IF subjective probability of audit is lower than lower-bound of perceived risk;
        # 2) actual income ONLY IF penalty_rate * subjective probability of audit is higher than tax rate;
        # 3) a fraction of actual income based on subjective probability of audit, considering tax and penalty
        # rates and personal risk aversion
        elif self.__state == "Dishonest":
            # Get model's global variables that apply to all the following functions
            tax_rate = model.tax_rate
            penalty_rate = model.penalty_rate

            # Set the lower bound for what the person will declare
            self.__lower_bound = (tax_rate / (tax_rate + (penalty_rate - tax_rate) **
                                              (self.__risk_aversion * penalty_rate * self.__actual_income)))

            # lower_bound represents the minimum risk necessary to convince the agent to declare its actual income
            # accurately.  If the agent's perceived probability of an audit is below that lower_bound, dishonest
            # agents won't declare any income at all
            if self.__ps_value < self.__lower_bound:
                self.__declared_income = 0
            # If interaction of penalty with subjective probability of audit is higher than the tax rate,
            # better off declaring actual income.
            elif penalty_rate * self.__ps_value > tax_rate:
                self.__declared_income = self.__actual_income
            # Otherwise, dishonesty shines. Actual income is reduced as a function of agent's individual tax aversion
            # rate, indiv. subjective probability of audit, and global tax and penalty rates.
            else:
                self.__declared_income = self.__actual_income - \
                                         (np.log(abs(((1.0 - self.__ps_value) * tax_rate) /
                                                     (self.__ps_value * (-1 * tax_rate + penalty_rate))) /
                                                 (self.__risk_aversion * penalty_rate)))

    def audit_check(self):
        """
        Tests whether the agent is audited at this timestep and, if so, 
        adjust declared income accordingly and set audit count to max and 
        subjective probability of audit to 1.0.
        """

        # Access the model
        model = self.get_model()

        # if there have been audits, decrease by 1
        if self.__audit_count > 0:
            self.__audit_count -= 1

        # If subjective probability is higher than model's global probaility of audit, reduce subjective
        # probability by 0.2
        if self.__ps_value > model.audit_prob:
            self.__ps_value -= 0.2

        # Else, if it's lower, set it to the global probability (global value is the minimum for an agent)
        elif self.__ps_value < model.audit_prob:
            self.__ps_value = model.audit_prob
            
        # Get model's global variables that apply to all the following functions
        tax_rate = model.get_element(model.tax_rate)
        penalty_rate = model.get_element(model.penalty_rate)
        apprehension_on = model.get_element(model.apprehension)

        # Korobow model heuristic
        if apprehension_on:
            if npr.uniform(size=1)[0] < model.apprehensionRate:
                if self.__declared_income < self.__actual_income:
                    self.__apprehended = True
                    self.__declared_income = tax_rate * (self.__actual_income - self.__declared_income) \
                                           * (1.0 + penalty_rate * self.__actual_income)
                    self.__ps_value = 1.0
                else:
                    self.__apprehended = False

        # Hokamp penalty equation
        else:
            if self.__declared_income < self.__actual_income:
                audit_probability = model.get_element(model.audit_prob)
                audit_max = model.get_element(model.max_audit)
                if npr.uniform(size=1)[0] <= audit_probability:
                    self.__declared_income = self.__actual_income + self.__declared_income * penalty_rate / tax_rate
                    self.__audit_count = audit_max
                    self.__ps_value = 1.0

    def update(self):
        """
        Update the person to calculate declared income and whether person is 
        audited, resulting in possible apprehension. 
        """
        model = self.get_model()

        old_declared_income = self.__declared_income
        self.update_declared_income()
        self.audit_check()
        self.add_event(model.get_time()+1)
        if old_declared_income == self.__declared_income:
            eid = self.get_element_id()
            model.element_state_change(eid)

        return self.__declared_over_actual

    def get_element_requests(self):
        for i in self.__neighbors:
            self.get_model().request_element(i)
        return
