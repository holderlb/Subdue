# OrderedSet.py
#
# Written by Larry Holder (holder@wsu.edu).
#
# Copyright (c) 2017-2021. Washington State University.
#
# This implementation of OrderedSet maintains the set as both an
# actual (unordered) Python set and an ordered list. The main
# difference from other OrderedSet containers is that equality
# is supported.

class OrderedSet:

    def __init__(self, arg = None):
        if arg is None:
            arg = []
        self.list_container = []
        self.set_container = set()
        elements = []
        if isinstance(arg, (list, set)):
            elements = arg
        if isinstance(arg, OrderedSet):
            elements = arg.list_container
        for x in elements:
            self.add(x)
    
    def __str__(self):
        s = '{'
        firstOne = True
        for x in self.list_container:
            if firstOne:
                firstOne = False
            else:
                s += ', '
            s += str(x)
        s += '}'
        return s
        
    def __iter__(self):
        self.list_index = 0
        return self
    
    def __next__(self):
        if self.list_index >= len(self.list_container):
            raise StopIteration
        x = self.list_container[self.list_index]
        self.list_index += 1
        return x
    
    def __sub__(self, other):
        diff_set = self.set_container - other.set_container
        elements = [x for x in self.list_container if x in diff_set]
        return OrderedSet(elements)
    
    def __add__(self, other):
        new_set = OrderedSet(self.list_container)
        diff_set = other.set_container - self.set_container
        other_elements = [x for x in other.list_container if x in diff_set]
        for x in other_elements:
            new_set.add(x)
        return new_set
    
    def __eq__(self, other):
        return (self.set_container == other.set_container)
    
    def __ne__(self, other):
        return (self.set_container != other.set_container)
    
    def add(self, x):
        if x not in self.set_container:
            self.list_container.append(x)
            self.set_container.add(x)
    
    def intersect(self, other):
        if self.set_container.intersection(other.set_container):
            return True
        else:
            return False
    
    def intersection(self, other):
        int_set = self.set_container.intersection(other.set_container)
        elements = [x for x in self.list_container if x in int_set]
        return OrderedSet(elements)
    
