__author__ = 'jgentile'

import mabm
import abc

class Container:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_element(self,element):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def remove_element(self,element):
        pass

    @abc.abstractmethod
    def get_element_requests(self):
        pass
