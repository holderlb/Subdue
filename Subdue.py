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
import Pattern

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
   
def DiscoverPatterns(parameters, graph):
    """The main discovery loop. Finds and returns best patterns in given graph."""
    patternCount = 0
    # get initial one-edge patterns
    parentPatternList = GetInitialPatterns(graph, parameters.temporal)
    if DEBUGFLAG:
        print "Initial patterns (" + str(len(parentPatternList)) + "):"
        for pattern in parentPatternList:
            pattern.print_pattern('  ')
    discoveredPatternList = []
    while ((patternCount < parameters.limit) and parentPatternList):
        print str(parameters.limit - patternCount) + " patterns left"
        childPatternList = []
        # extend each pattern in parent list (***** todo: in parallel)
        while (parentPatternList):
            parentPattern = parentPatternList.pop(0)
            if ((len(parentPattern.instances) > 1) and (patternCount < parameters.limit)):
                patternCount += 1
                extendedPatternList = Pattern.ExtendPattern(parentPattern, parameters.temporal)
                while (extendedPatternList):
                    extendedPattern = extendedPatternList.pop(0)
                    if DEBUGFLAG:
                        print "Extended Pattern:"
                        extendedPattern.print_pattern('  ')
                    if (len(extendedPattern.definition.edges) <= parameters.maxSize):
                        # evaluate each extension and add to child list
                        extendedPattern.evaluate(graph)
                        if ((not parameters.prune) or (extendedPattern.value >= parentPattern.value)):
                            Pattern.PatternListInsert(extendedPattern, childPatternList, parameters.beamWidth, parameters.valueBased)
            # add parent pattern to final discovered list
            if (len(parentPattern.definition.edges) >= parameters.minSize):
                Pattern.PatternListInsert(parentPattern, discoveredPatternList, parameters.numBest, False) # valueBased = False
        parentPatternList = childPatternList
    # insert any remaining patterns in parent list on to discovered list
    while (parentPatternList):
        parentPattern = parentPatternList.pop(0)
        if (len(parentPattern.definition.edges) >= parameters.minSize):
            Pattern.PatternListInsert(parentPattern, discoveredPatternList, parameters.numBest, False) # valueBased = False
    return discoveredPatternList

def GetInitialPatterns(graph, temporal = False):
    """Returns list of single-edge, evaluated patterns in given graph with more than one instance."""
    initialPatternList = []
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
            # Create initial pattern
            pattern = Pattern.Pattern()
            pattern.definition = Graph.CreateGraphFromEdge(matchingEdges[0])
            if temporal:
                pattern.definition.TemporalOrder()
            pattern.instances = []
            for edge in matchingEdges:
                pattern.instances.append(Pattern.CreateInstanceFromEdge(edge))
            pattern.evaluate(graph)
            initialPatternList.append(pattern)
        candidateEdges = nonmatchingEdges
    return initialPatternList

def Subdue(parameters, graph):
    """Top-level function for Subdue that discovers best pattern in graph.
       Optionally, Subdue can then compress the graph with the best pattern, and iterate."""
    startTime = time.time()
    iteration = 1
    done = False
    while ((iteration <= parameters.iterations) and (not done)):
        iterationStartTime = time.time()
        if (iteration > 1):
            print "----- Iteration " + str(iteration) + " -----\n"
        print "Graph: " + str(len(graph.vertices)) + " vertices, " + str(len(graph.edges)) + " edges"
        patternList = DiscoverPatterns(parameters, graph)
        if (not patternList):
            done = True
            print "No patterns found.\n"
        else:
            print "\nBest " + str(len(patternList)) + " patterns:\n"
            for pattern in patternList:
                pattern.print_pattern('  ')
                print
            # write machine-readable output, if requested
            if (parameters.writePattern):
                outputFileName = parameters.outputFileName + "-pattern-" + str(iteration) + ".json"
                patternList[0].definition.write_to_file(outputFileName)
            if (parameters.writeInstances):
                outputFileName = parameters.outputFileName + "-instances-" + str(iteration) + ".json"
                patternList[0].write_instances_to_file(outputFileName)
            if ((iteration < parameters.iterations) or (parameters.writeCompressed)):
                graph.Compress(iteration, patternList[0])
            if (iteration < parameters.iterations):
                # consider another iteration
                if (len(graph.edges) == 0):
                    done = True
                    print "Ending iterations - graph fully compressed.\n"
            if ((iteration == parameters.iterations) and (parameters.writeCompressed)):
                outputFileName = parameters.outputFileName + "-compressed-" + str(iteration) + ".json"
                graph.write_to_file(outputFileName)
        if (parameters.iterations > 1):
             iterationEndTime = time.time()
             print "Elapsed time for iteration " + str(iteration) + " = " + str(iterationEndTime - iterationStartTime) + " seconds.\n"
        iteration += 1
    endTime = time.time()
    print "SUBDUE done. Elapsed time = " + str(endTime - startTime) + " seconds\n"
    
def main():
    print "SUBDUE v1.0 (python)\n"
    parameters = Parameters.Parameters()
    parameters.set_parameters(sys.argv)
    graph = ReadGraph(parameters.inputFileName)
    #outputFileName = parameters.outputFileName + ".dot"
    #graph.write_to_dot(outputFileName)
    if (parameters.limit == 0):
        parameters.limit = len(graph.edges) / 2
    if (parameters.maxSize == 0):
        parameters.maxSize = len(graph.edges) / 2
    if (parameters.iterations == 0):
        parameters.iterations = len(graph.edges)
    Subdue(parameters, graph)

if __name__ == "__main__":
    main()
