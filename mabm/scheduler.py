__author__ = 'jgentile', 'ceharvey'

import sys
from collections import OrderedDict
import random


class Scheduler:
    __time_series = None

    def __init__(self):
        """"
        Initialize a scheduler for the MABM module
        """
        self.__time_series = OrderedDict()

    def add_event(self, time, element):
        """
        Use a time and an element to add an event to the model.
        """
        try:
            self.__time_series[time].append(element)
        except KeyError:
            self.__time_series[time] = [element]

    def get_next_event_time(self):
        """
        Find the next event time.
        """
        if len(self.__time_series):
            # Return the minimum value in the list of event times
            return min(self.__time_series)
        else:
            return sys.maxint

    def update(self, time):
        """
        Update the elements in the model.  Go through the chosen time in self.__time_series
        and for each element in the series, update the element and remove the item from
        the list of items to be updated.
        """
        if time in self.__time_series:
            # Shuffle the list in place, for random activation
            random.shuffle(self.__time_series[time])
            for e in self.__time_series[time]:
                e.update()
            self.__time_series.popitem(last=False)

    def get_element_requests(self, time):
        """
        Complete the element requests for each element in the time series.
        """
        if time in self.__time_series:
            for e in self.__time_series[time]:
                e.get_element_requests()