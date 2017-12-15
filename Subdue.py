# Subdue.py
#
# Written by Larry Holder (holder@wsu.edu).
#
# Copyright (c) 2017. Washington State University.

import sys
import time
import json
import Parameters
import Graph
import Substructure

DEBUGFLAG = False

# ***** todos: read graph file incrementally
def ReadGraph(inputFileName):
    """Read graph from given filename."""
    inputFile = open(inputFileName)
    jsonGraphArray = json.load(inputFile)
    graph = Graph.Graph()
    graph.load_from_json(jsonGraphArray)
    inputFile.close()
    return graph
   
def DiscoverSubs(parameters, graph):
    """The main discovery loop. Finds and returns best substructures in given graph."""
    subCount = 0
    # get initial one-edge substructures
    parentSubList = GetInitialSubs(graph, parameters.temporal)
    if DEBUGFLAG:
        print "Initial subs (" + str(len(parentSubList)) + "):"
        for sub in parentSubList:
            sub.print_substructure('  ')
    discoveredSubList = []
    while ((subCount < parameters.limit) and parentSubList):
        childSubList = []
        # extend each substructure in parent list (***** todo: in parallel)
        while (parentSubList):
            parentSub = parentSubList.pop(0)
            if ((len(parentSub.instances) > 1) and (subCount < parameters.limit)):
                subCount += 1
                extendedSubList = Substructure.ExtendSub(parentSub, parameters.temporal)
                while (extendedSubList):
                    extendedSub = extendedSubList.pop(0)
                    if DEBUGFLAG:
                        print "Extended Substructure:"
                        extendedSub.print_substructure('  ')
                    if (len(extendedSub.definition.edges) <= parameters.maxSize):
                        # evaluate each extension and add to child list
                        extendedSub.evaluate(graph)
                        if ((not parameters.prune) or (extendedSub.value >= parentSub.value)):
                            Substructure.SubListInsert(extendedSub, childSubList, parameters.beamWidth, parameters.valueBased)
            # add parent substructure to final discovered list
            if (len(parentSub.definition.edges) >= parameters.minSize):
                Substructure.SubListInsert(parentSub, discoveredSubList, parameters.numBestSubs, False) # valueBased = False
        parentSubList = childSubList
    # insert any remaining subs in parent list on to discovered list
    while (parentSubList):
        parentSub = parentSubList.pop(0)
        if (len(parentSub.definition.edges) >= parameters.minSize):
            Substructure.SubListInsert(parentSub, discoveredSubList, parameters.numBestSubs, False) # valueBased = False
    return discoveredSubList

def GetInitialSubs(graph, temporal = False):
    """Returns list of single-edge, evaluated substructures in given graph with more than one instance."""
    initialSubList = []
    candidateEdges = graph.edges.values()
    while candidateEdges:
        edge1 = candidateEdges.pop(0)
        matchingEdges = [edge1]
        nonmatchingEdges = []
        for edge2 in candidateEdges:
            if ((edge1.directed == edge2.directed) and
                (cmp(edge1.attributes, edge2.attributes) == 0) and
                (cmp(edge1.source.attributes, edge2.source.attributes) == 0) and
                (cmp(edge1.target.attributes, edge2.target.attributes) == 0)): # ignoring timestamps
                matchingEdges.append(edge2)
            else:
                nonmatchingEdges.append(edge2)
        if len(matchingEdges) > 1:
            # Create initial substructure
            sub = Substructure.Substructure()
            sub.definition = Graph.CreateGraphFromEdge(matchingEdges[0])
            if temporal:
                sub.definition.TemporalOrder()
            sub.instances = []
            for edge in matchingEdges:
                sub.instances.append(Substructure.CreateInstanceFromEdge(edge))
            sub.evaluate(graph)
            initialSubList.append(sub)
        candidateEdges = nonmatchingEdges
    return initialSubList

def Subdue(parameters, graph):
    """Top-level function for Subdue that discovers best substructure in graph.
    Optionally, Subdue can then compress the graph with the best substructure, and iterate."""
    startTime = time.time()
    iteration = 1
    done = False
    while ((iteration <= parameters.iterations) and (not done)):
        iterationStartTime = time.time()
        if (iteration > 1):
            print "----- Iteration " + str(iteration) + " -----\n"
        print "Graph: " + str(len(graph.vertices)) + " vertices, " + str(len(graph.edges)) + " edges"
        subList = DiscoverSubs(parameters, graph)
        if (not subList):
            done = True
            print "No substructures found.\n"
        else:
            print "\nBest " + str(len(subList)) + " substructures:\n"
            for sub in subList:
                sub.print_substructure('  ')
                print
            # write machine-readable output, if requested
            if (parameters.writeSub):
                outputFileName = parameters.outputFileName + "-sub-" + str(iteration) + ".json"
                subList[0].definition.write_to_file(outputFileName)
            if (parameters.writeInsts):
                outputFileName = parameters.outputFileName + "-insts-" + str(iteration) + ".json"
                subList[0].write_instances_to_file(outputFileName)
            if ((iteration < parameters.iterations) or (parameters.writeCompressed)):
                graph.Compress(iteration, subList[0])
            if (iteration < parameters.iterations):
                # consider another iteration
                if (len(graph.edges) == 0):
                    done = True
                    print "Ending iterations - graph fully compressed.\n"
            if ((iteration == parameters.iterations) and (parameters.writeCompressed)):
                outputFileName = parameters.outputFileName + "-cmp-" + str(iteration) + ".json"
                graph.write_to_file(outputFileName)
        if (parameters.iterations > 1):
             iterationEndTime = time.time()
             print "Elapsed time for iteration " + str(iteration) + " = " + str(iterationEndTime - iterationStartTime) + " seconds.\n"
        iteration += 1
    endTime = time.time()
    print "SUBDUE done. Elapsed time = " + str(endTime - startTime) + " seconds"
    
def SubdueTest(parameters, graph):
    print "Testing"
    print "  Test #1 (match input graph to itself):",
    if (Graph.Match(graph,graph)):
        print "PASS"
    else:
        print "FAIL"
    print "  Test #2 (check non-isomorphic graphs):",
    g1 = ReadGraph("testgraph1.json")
    g2 = ReadGraph("testgraph2.json")
    if (Graph.Match(g1,g2)):
        print "FAIL"
    else:
        print "PASS"
    
def main():
    print "Subdue v1.0 (python)"
    parameters = Parameters.Parameters()
    parameters.set_parameters(sys.argv)
    graph = ReadGraph(parameters.inputFileName)
    outputFileName = parameters.outputFileName + ".dot"
    graph.write_to_dot(outputFileName)
    if (parameters.limit == 0):
        parameters.limit = len(graph.edges) / 2
    if (parameters.maxSize == 0):
        parameters.maxSize = len(graph.edges) / 2
    if (parameters.iterations == 0):
        parameters.iterations = len(graph.edges)
    #SubdueTest(parameters, graph)
    Subdue(parameters, graph)

if __name__ == "__main__":
    main()
