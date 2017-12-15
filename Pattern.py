# Substructure.py
#
# Written by Larry Holder (holder@wsu.edu).
#
# Copyright (c) 2017. Washington State University.

import Graph

class Substructure:
    
    def __init__(self):
        self.definition = None # Graph
        self.instances = []
        self.value = 0.0
    
    def evaluate (self, graph):
        """Compute value of using given substructure to compress given graph, where 0 means no compression, and 1 means perfect compression."""
        # (instances-1) because we would also need to retain the definition of the substructure for compression
        self.value = float(((len(self.instances) - 1) * len(self.definition.edges)) / float(len(graph.edges))) 
    
    def print_substructure(self, tab):
        print tab + "Substructure (value=" + str(self.value) + ", instances=" + str(len(self.instances)) + "):"
        self.definition.print_graph(tab+'  ')
        # May want to make instance printing optional
        instanceNum = 1
        for instance in self.instances:
            instance.print_instance(instanceNum, tab+'  ')
            instanceNum += 1
    
    def write_instances_to_file(self, outputFileName):
        """Write instances of substructure to given file name in JSON format."""
        outputFile = open(outputFileName, 'w')
        outputFile.write('[\n')
        firstOne = True
        for instance in self.instances:
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            instance.write_to_file(outputFile)
        outputFile.write('\n]\n')
        outputFile.close()

class Instance:
    
    def __init__(self):
        self.vertices = []
        self.edges = []
    
    def print_instance (self, instanceNum, tab=""):
        print tab + "Instance " + str(instanceNum) + ":"
        for vertex in self.vertices:
            vertex.print_vertex(tab+'  ')
        for edge in self.edges:
            edge.print_edge(tab+'  ')
            
    def write_to_file(self, outputFile):
        """Write instance to given file stream in JSON format."""
        firstOne = True
        for vertex in self.vertices:
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            vertex.write_to_file(outputFile)
        outputFile.write(',\n')
        firstOne = True
        for edge in self.edges:
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            edge.write_to_file(outputFile)
    
    def max_timestamp(self):
        """Returns the maximum timestamp over all vertices and edges in the instance."""
        maxTimeStamp = 0
        for vertex in self.vertices:
            if (vertex.timestamp > maxTimeStamp):
                maxTimeStamp = vertex.timestamp
        for edge in self.edges:
            if (edge.timestamp > maxTimeStamp):
                maxTimeStamp = edge.timestamp
        return maxTimeStamp
        

# ----- Substructure and Instance Creation
 
def CreateInstanceFromEdge(edge):
    i = Instance()
    i.edges = [edge]
    i.vertices = [edge.source, edge.target]
    return i

def CreateSubFromInstances(definition, instances):
    """Create substructure from given definition graph and its instances. Note: Substructure not evaluated here."""
    sub = Substructure()
    sub.definition = definition
    sub.instances = instances
    return sub

# ----- Substructure Extension

def ExtendSub (sub, temporal = False):
    """Return list of substructures created by extending each instance of the given substructure by one edge in all possible ways,
       and then collecting matching extended instances together into new substructures."""
    extendedInstances = []
    for instance in sub.instances:
        newInstances = ExtendInstance(instance)
        for newInstance in newInstances:
            InsertNewInstance(extendedInstances, newInstance)
    newSubs = []
    while extendedInstances:
        newInstance = extendedInstances.pop(0)
        newInstanceGraph = Graph.CreateGraphFromInstance(newInstance)
        if temporal:
            newInstanceGraph.TemporalOrder()
        matchingInstances = [newInstance]
        nonmatchingInstances = []
        for extendedInstance in extendedInstances:
            extendedInstanceGraph = Graph.CreateGraphFromInstance(extendedInstance)
            if temporal:
                extendedInstanceGraph.TemporalOrder()
            if Graph.GraphMatch(newInstanceGraph,extendedInstanceGraph) and (not InstancesOverlap(matchingInstances,extendedInstance)):
                matchingInstances.append(extendedInstance)
            else:
                nonmatchingInstances.append(extendedInstance)
        extendedInstances = nonmatchingInstances
        newSub = CreateSubFromInstances(newInstanceGraph, matchingInstances)
        newSubs.append(newSub)
    return newSubs

def ExtendInstance (instance):
    """Returns list of new instances created by extending the given instance by one new edge in all possible ways."""
    usedEdges = list(instance.edges)
    newInstances = []
    for vertex in instance.vertices:
        for edge in vertex.edges:
            if (not edge in usedEdges):
                newInstance = ExtendInstanceByEdge(instance, edge)
                newInstances.append(newInstance)
                usedEdges.append(edge)
    return newInstances

def ExtendInstanceByEdge(instance, edge):
    """Create and return new instance built from given instance and adding given edge and vertices of edge if new"""
    newInstance = Instance()
    newInstance.vertices = list(instance.vertices)
    newInstance.edges = list(instance.edges)
    newInstance.edges.append(edge)
    if (not edge.source in newInstance.vertices):
        newInstance.vertices.append(edge.source)
    if (not edge.target in newInstance.vertices):
        newInstance.vertices.append(edge.target)
    return newInstance

def InsertNewInstance(instanceList, newInstance):
    """Add newInstance to instanceList if it does not match an instance already on the list."""
    match = False
    for instance in instanceList:
        if (InstanceMatch(instance,newInstance)):
            match = True
            break
    if not match:
        instanceList.append(newInstance)

def InstanceMatch(instance1,instance2):
    """Return True if given instances match, i.e., contain the same vertex and edge object instances."""
    if (len(instance1.vertices) != len(instance2.vertices)):
        return False
    if (len(instance1.edges) != len(instance2.edges)):
        return False
    for vertex1 in instance1.vertices:
        if not vertex1 in instance2.vertices:
            return False
    for edge1 in instance1.edges:
        if not edge1 in instance2.edges:
            return False
    return True

def InstancesOverlap(instanceList,instance):
    """Returns True if instance contains a vertex that is contained in an instance of the given instanceList."""
    for instance2 in instanceList:
        if InstanceOverlap(instance,instance2):
            return True
    return False

def InstanceOverlap(instance1,instance2):
    """Returns True if given instances share a vertex."""
    for vertex1 in instance1.vertices:
        if vertex1 in instance2.vertices:
            return True
    return False

# ----- Substructure List Operations

def SubListInsert(newSub, subList, maxLength, valueBased):
    """Insert newSub into subList. If newSub is isomorphic to an existing substructure on subList, then keep higher-valued substructure.
       List is kept in decreasing order by substructure value. If valueBased=True, then maxLength represents the maximum number
       of different-valued substructures on the list; otherwise, maxLength represents the maximum number of substructures on
       the list. Assumes given subList already conforms to maximums."""
    # Check if newSub unique (i.e., non-isomorphic or isomorphic but better-valued)
    for sub in subList:
        if (Graph.GraphMatch(sub.definition,newSub.definition)):
            if (sub.value >= newSub.value):
                return # newSub already on list with same or better value
            else:
                # newSub isomorphic to existing sub, but better valued
                subList.remove(sub)
                break
    # newSub unique, so insert in order by value
    insertAtIndex = 0
    for sub in subList:
        if newSub.value > sub.value:
            break
        insertAtIndex += 1
    subList.insert(insertAtIndex, newSub)
    # check if subList needs to be trimmed
    if valueBased:
        uniqueValues = UniqueValues(subList)
        if len(uniqueValues) > maxLength:
            removeValue = uniqueValues[-1]
            while (subList[-1].value == removeValue):
                subList.pop(-1)
    else:
        if len(subList) > maxLength:
            subList.pop(-1)
