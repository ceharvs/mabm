__author__ = 'jgentile', 'ceharvey'

import mabm


class ElementIDGenerator:
    __type_dict = None
    __type_number = None
    __process = None

    def __init__(self, process, type_dict):
        """Initialize an element_id generator"""
        self.__type_dict = {}
        self.__enum_form_dict = {}
        self.__type_number = {}
        self.__process = process

        # For each key given in type_dict, set up the
        # self.__type_dict and self.__enum_form_dict dictionaries
        for key in type_dict:
            self.__type_dict[type_dict[key][0]] = key
            self.__enum_form_dict[key] = type_dict[key][1]

        # Set the self.__type_number dictionary to contain zero values for all
        # lookup values
        for key in self.__type_dict.keys():
            self.__type_number[key] = 0

    def get_new_element_id(self, type):
        """Get the element_id for a new element"""
        if type in self.__type_number:
            e = mabm.ElementID(self.__type_dict[type], self.__type_number[type], self.__process)
            self.__type_number[type] += 1
            return e

        else:
            print 'Error in ElementIDGenerator.get_element_id, type',type,'not in __type_dictionary.'

    def get_form_from_type(self,type):
        """Get the enum_form from the element type"""
        return self.__enum_form_dict[type]

