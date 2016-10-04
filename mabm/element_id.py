__author__ = 'jgentile', 'ceharvey'



class ElementID:
    # Slots functionality implemented to conserve memory
    __slots__ = ['__type', '__number', '__process', '__birth_process', '__serialed']

    def __init__(self, type_or_str, number=None, process=None, birth_process=None):
        """Create an elementID using a serialized element string or
        using specific factors from the optional arguments
        """
        self.__serialed = None

        # If the element instance is a string, this serialized information
        # which is then split and assigned to the values
        if isinstance(type_or_str, str):
            a = type_or_str.split('|')
            self.__type = int(a[0])
            self.__number = int(a[1])
            self.__process = int(a[2])
            self.__birth_process = int(a[3])
            return

        # If the element instance is not a string, use the input arguments
        # to generate information about the element
        self.__type = type_or_str
        self.__number = number
        self.__process = process
        if not birth_process:
            self.__birth_process = process
        else:
            self.__birth_process = birth_process

    def __str__(self):
        """Return a serialized version of the agent"""
        return self.serialize()

    def serialize(self):
        """Return a serialized version of the element"""
        # Check if the element has already been serialized
        if not self.__serialed:
            self.__serialed = str(self.__type)+'|'+str(self.__number)+'|'+str(self.__process)+'|'\
                              +str(self.__birth_process)
        return self.__serialed

    def set_process(self,process):
        """Set the process number in the element_id"""
        self.__process = process
        self.__serialed = None

    def get_process(self):
        """Return the current process of the element"""
        return self.__process

    def get_type(self):
        """Return the type of the element"""
        return self.__type

    def get_number(self):
        """Get the number of the agent from the element_id"""
        return self.__number
