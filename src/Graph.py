# Graph.py
#
# Written by Larry Holder (holder@wsu.edu).
#
# Copyright (c) 2017-2021. Washington State University.

import json
        
# The Graph class allows the representation of an attributed, mixed multi-graph with time stamps on nodes
# and edges. A graph has an id and a className (for now, either "positive" or "negative"). Each node has
# an id and a timestamp, along with other user-defined attributes. Each edge has an id, source, target,
# directed, and timestamp, along with other user-defined attributes.
# Note: Assumes time stamps are integers.
class Graph:
    
    def __init__(self):
        self.vertices = {}
        self.edges = {}
    
    def Compress(self,iteration,pattern):
        """Compress graph using given pattern at given iteration. Replaces each instance of pattern with a new
           vertex, and reconnects edges incident on the instance to the new vertex. Assumes no overlap among instances."""
        instanceNum = 0
        for instance in pattern.instances:
            instanceNum += 1
            # Create and add new vertex representing pattern instance
            newVertexLabel = 'PATTERN-' + str(iteration)
            newVertexId = 'PATTERN-' + str(iteration) + '-' + str(instanceNum)
            newVertex = Vertex(newVertexId)
            newVertex.timestamp = instance.max_timestamp()
            newVertex.add_attribute('label', newVertexLabel)
            self.vertices[newVertexId] = newVertex
            # Remove instance's edges from graph and from source/target vertex edge lists
            for instanceEdge in instance.edges:
                instanceEdge.source.edges.remove(instanceEdge)
                instanceEdge.target.edges.remove(instanceEdge)
                del self.edges[instanceEdge.id]
            # Remove instance's vertices from graph; remaining edges incident on this vertex should be made incident on newVertex
            for instanceVertex in instance.vertices:
                for edge in instanceVertex.edges:
                    if edge.source == instanceVertex:
                        edge.source = newVertex
                    if edge.target == instanceVertex:
                        edge.target = newVertex
                    if edge not in newVertex.edges:
                        newVertex.edges.append(edge)
                del self.vertices[instanceVertex.id]

    def TemporalOrder(self):
        """Set the temporal property of vertices and edges according to their order of arrival."""
        # Collect and sort all unique timestamps in graph
        timestamps = []
        for vertex in self.vertices.values():
            if vertex.timestamp not in timestamps:
                timestamps.append(vertex.timestamp)
        for edge in self.edges.values():
            if edge.timestamp not in timestamps:
                timestamps.append(edge.timestamp)
        timestamps.sort()
         # Set temporal property based on order of timestamp
        for vertex in self.vertices.values():
            vertex.temporal = timestamps.index(vertex.timestamp)
        for edge in self.edges.values():
            edge.temporal = timestamps.index(edge.timestamp)

    # Load graph from given JSON array of vertices and edges.
    # ***** todo: Read graph from stream, rather than all at once
    def load_from_json (self, jsonGraphArray):
        # Initialize graph (just in case it's being reused)
        self.vertices = {}
        self.edges = {}
        for json_object in jsonGraphArray:
            if ('vertex' in json_object):
                vertexDict = json_object['vertex']
                vertexId = vertexDict['id']
                if (vertexId not in self.vertices): # in case fused graph with duplicate vertices
                    vertex = Vertex(vertexId)
                    if ('timestamp' in vertexDict):
                        vertex.timestamp = int(vertexDict['timestamp'])
                    if ('attributes' in vertexDict):
                        json_attrs = vertexDict['attributes']
                        for key,value in json_attrs.items():
                            vertex.add_attribute(key, value)
                    self.vertices[vertexId] = vertex
            if ('edge' in json_object):
                edgeDict = json_object['edge']
                edgeId = edgeDict['id']
                sourceId = edgeDict['source']
                targetId = edgeDict['target']
                sourceVertex = self.vertices[sourceId]
                targetVertex = self.vertices[targetId]
                directed = False
                if (edgeDict['directed'] == 'true'):
                    directed = True
                edge = Edge(edgeId, sourceVertex, targetVertex, directed)
                if ('timestamp' in edgeDict):
                    edge.timestamp = int(edgeDict['timestamp'])
                if ('attributes' in edgeDict):
                    json_attrs = edgeDict['attributes']
                    for key,value in json_attrs.items():
                        edge.add_attribute(key,value)
                self.edges[edgeId] = edge
                sourceVertex.add_edge(edge)
                targetVertex.add_edge(edge)

    def load_from_networkx(
        self,
        networkx_graph,
        node_attributes=None,
        edge_attributes=None,
    ):
        # helper routine
        def select_attributes_from_dict(dict_, attributes=None):
            if attributes is None:
                return dict_
            else:
                return {attr: dict_[attr] for attr in attributes}

        directed = networkx_graph.is_directed
        subdue_format = list()
        for node_id in networkx_graph.nodes:
            subdue_format.append({
                'vertex': {
                    'id': node_id,
                    'attributes': select_attributes_from_dict(networkx_graph.nodes[node_id], node_attributes).copy(),
                }
            })
        for (u, v) in networkx_graph.edges():
            subdue_format.append({
                'edge': {
                    'id': f'{u}-{v}',
                    'source': u,
                    'target': v,
                    'directed': directed,
                    'attributes': select_attributes_from_dict(networkx_graph.edges[(u, v)], edge_attributes).copy(),
                }
            })

        self.load_from_json(subdue_format)

    def write_to_dot(self, outputFileName):
        """Write graph to given file name in DOT format."""
        outputFile = open(outputFileName, 'w')
        outputFile.write('digraph {\n')
        for vertex in self.vertices.values():
            labelStr = str(vertex.id)
            if ('label' in vertex.attributes):
                labelStr = str(vertex.attributes['label'])
            outputFile.write(str(vertex.id) + ' [label=' + labelStr + '];\n')
        for edge in self.edges.values():
            labelStr = str(edge.id)
            if ('label' in edge.attributes):
                labelStr = str(edge.attributes['label'])
            outputStr = str(edge.source.id) + ' -> ' + str(edge.target.id) + ' [label=' + labelStr
            if (not edge.directed):
                outputStr += ',dir=none'
            outputStr += '];\n'
            outputFile.write(outputStr)
        outputFile.write('}\n')
        outputFile.close()
    
    def write_to_file(self, outputFileName):
        """Write graph to given file name in JSON format."""
        outputFile = open(outputFileName, 'w')
        outputFile.write('[\n')
        firstOne = True
        for vertex in self.vertices.values():
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            vertex.write_to_file(outputFile)
        outputFile.write(',\n')
        firstOne = True
        for edge in self.edges.values():
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            edge.write_to_file(outputFile)
        outputFile.write('\n]\n')
        outputFile.close()
    
    def print_graph(self, tab=""):
        print(tab + "Graph:")
        for vertex in self.vertices.values():
            vertex.print_vertex(tab+'  ')
        for edge in self.edges.values():
            edge.print_edge(tab+'  ')

class Vertex:
    
    def __init__(self, id):
        self.id = id # must be unique for each vertex
        self.timestamp = 0
        self.temporal = 0 # used to set arrival order of vertex internally for graph matcher
        self.attributes = {}
        self.edges = []
    
    def add_attribute(self, key, value):
        self.attributes[key] = value
    
    def add_edge(self, edge):
        self.edges.append(edge)
    
    def print_vertex(self, tab=""):
        attributeString = ""
        for key,value in self.attributes.items():
            attributeString += ', ' + key + '=' + str(value)
        print(tab + 'vertex "' + self.id + '": timestamp=' + str(self.timestamp) + attributeString)
    
    def write_to_file(self, outputFile):
        """Write vertex to given file stream in JSON format"""
        outputFile.write('  {"vertex": {\n')
        outputFile.write('     "id": "' + self.id + '",\n')
        outputFile.write('     "attributes": {')
        firstOne = True
        for key,value in self.attributes.items():
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',')
            outputFile.write('"' + key + '": "' + value + '"')
        outputFile.write('},\n')
        outputFile.write('     "timestamp": "' + str(self.timestamp) + '"}}')

class Edge:

    def __init__(self, id, source, target, directed = False):
        self.id = id # must be unique for each edge
        self.source = source
        self.target = target
        self.directed = directed
        self.timestamp = 0
        self.temporal = 0 # used to set arrival order of edge internally for graph matcher
        self.attributes = {}
        
    def add_attribute(self, key, value):
        self.attributes[key] = value
    
    def print_edge(self, tab=""):
        attributeString = ""
        for key,value in self.attributes.items():
            attributeString += ', ' + key + '=' + str(value)
        edgeString = self.source.id
        if self.directed:
            edgeString += '->'
        else:
            edgeString += '--'
        edgeString += self.target.id
        print(tab + 'edge "' + self.id + '" (' + edgeString + '): timestamp=' + str(self.timestamp) + attributeString)
        
    def write_to_file(self, outputFile):
        """Write edge to given file stream in JSON format"""
        outputFile.write('  {"edge": {\n')
        outputFile.write('     "id": "' + self.id + '",\n')
        outputFile.write('     "source": "' + self.source.id + '",\n')
        outputFile.write('     "target": "' + self.target.id + '",\n')
        outputFile.write('     "attributes": {')
        firstOne = True
        for key,value in self.attributes.items():
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',')
            outputFile.write('"' + key + '": "' + value + '"')
        outputFile.write('},\n')
        if self.directed:
            outputFile.write('     "directed": "true",\n')
        else:
            outputFile.write('     "directed": "false",\n')
        outputFile.write('     "timestamp": "' + str(self.timestamp) + '"}}')


# ----- Graph matcher

# New in version 1.2: poly-time-bounded graph matcher

gMaxMappings = 1 # Will be set to E^2 for each match

def GraphMatch(graph1, graph2):
    """Returns True if given graphs are isomorphic.
    This is a poly-time, approximate version of graph isomorphism."""
    global gMaxMappings
    if (len(graph1.vertices) != len(graph2.vertices)):
        return False
    if (len(graph1.edges) != len(graph2.edges)):
        return False
    if (len(graph1.edges) == 0):
        v1keys = list(graph1.vertices.keys())
        v2keys = list(graph2.vertices.keys())
        return MatchVertex(graph1, graph2, v1keys[0], v2keys[0])
    gMaxMappings = len(graph1.edges) ** 2 # Limit search to E^2 mappings
    matchFound, numMappings = ExtendMapping(graph1, graph2)
    return matchFound

def ExtendMapping(graph1, graph2, mapping=None, numMappings=0):
    """Find the next unmapped edge in graph1 and try mapping it to each unmapped edge in graph2.
    Constrain number of mappings to be at most gMaxMappings. Return the match result and
    number of mappings so far."""
    global gMaxMappings
    if mapping is None:
        mapping = {}
    if (len(mapping) == len(graph1.edges)):
        return True, numMappings
    if numMappings > gMaxMappings:
        return False, numMappings
    # Find unmapped edge in graph1 (should always exist at this point)
    edgeId1 = None
    for edgeId in graph1.edges:
        if (not (edgeId in mapping)):
            edgeId1 = edgeId
            break
    # Find unmapped, matching edge in graph2
    for edgeId2 in graph2.edges:
        if not (edgeId2 in mapping.values()):
            if MatchEdge(graph1, graph2, edgeId1, edgeId2, mapping):
                # Extend mapping
                mapping[edgeId1] = edgeId2
                matchFound, numMappings = ExtendMapping(graph1, graph2, mapping, numMappings + 1)
                if matchFound:
                    return True, numMappings
                mapping.pop(edgeId1)
    return False, numMappings

def GraphMatch_Orig(graph1, graph2):
    """Returns True if given graphs are isomorphic.
    This is a correct, non-approximate version of graph isomorphism."""
    if (len(graph1.vertices) != len(graph2.vertices)):
        return False
    if (len(graph1.edges) != len(graph2.edges)):
        return False
    if (len(graph1.edges) == 0):
        v1keys = list(graph1.vertices.keys())
        v2keys = list(graph2.vertices.keys())
        return MatchVertex(graph1, graph2, v1keys[0], v2keys[0])
    return ExtendMapping_Orig(graph1, graph2)

def ExtendMapping_Orig(graph1, graph2, mapping=None):
    """Find the next unmapped edge in graph1 and try mapping it to each unmapped edge in graph2.
    Return True if leads to a match, else False."""
    if mapping is None:
        mapping = {}
    if (len(mapping) == len(graph1.edges)):
        return True
    # Find unmapped edge in graph1 (should always exist at this point)
    edgeId1 = None
    for edgeId in graph1.edges:
        if (not (edgeId in mapping)):
            edgeId1 = edgeId
            break
    # Find unmapped, matching edge in graph2
    for edgeId2 in graph2.edges:
        if not (edgeId2 in mapping.values()):
            if MatchEdge(graph1,graph2,edgeId1,edgeId2,mapping):
                # Extend mapping
                mapping[edgeId1] = edgeId2
                if ExtendMapping_Orig(graph1,graph2,mapping):
                    return True
                mapping.pop(edgeId1)
    return False

def MatchEdge(graph1, graph2, edgeId1, edgeId2, mapping):
    """Return True if edges, corresponding to given edge IDs in given graphs, match;
    i.e., have same attributes, direction, temporal ordering, and source/target vertices."""
    edge1 = graph1.edges[edgeId1]
    edge2 = graph2.edges[edgeId2]
    if not (edge1.attributes == edge2.attributes):
        return False
    if (edge1.directed != edge2.directed):
        return False
    # Temporal field only set if discovering temporal patterns; otherwise, this test always True
    if (edge1.temporal != edge2.temporal):
        return False
    if (MatchVertex(graph1, graph2, edge1.source.id, edge2.source.id) and
        MatchVertex(graph1, graph2, edge1.target.id, edge2.target.id)):
        return True
    if ((not edge1.directed) and MatchVertex(graph1, graph2, edge1.source.id, edge2.target.id) and
        MatchVertex(graph1, graph2, edge1.target.id, edge2.source.id)):
        return True
    return False

def MatchVertex(graph1, graph2, vertexId1, vertexId2):
    """Returns True if vertices, corresponding to given vertex IDs in given graphs, match;
       i.e., same attributes and temporal edges."""
    # First check for same attributes
    vertex1 = graph1.vertices[vertexId1]
    vertex2 = graph2.vertices[vertexId2]
    if not (vertex1.attributes == vertex2.attributes):
        return False
    if (len(vertex1.edges) != len(vertex2.edges)):
        return False
    # Temporal field only set if discovering temporal patterns; otherwise, this test always True
    if (vertex1.temporal != vertex2.temporal):
        return False
    return True


# ----- Graph Creation

def CreateGraphFromEdge(edge):
    """Create a generic one-edge graph with the same properties as the given edge, but with new vertex/edge IDs."""
    g = Graph()
    source = Vertex("1")
    g.vertices["1"] = source
    source.timestamp = edge.source.timestamp
    source.attributes = edge.source.attributes
    target = Vertex("2")
    g.vertices["2"] = target
    target.timestamp = edge.target.timestamp
    target.attributes = edge.target.attributes
    e = Edge("1", source, target, edge.directed)
    g.edges["1"] = e
    e.timestamp = edge.timestamp
    e.attributes = edge.attributes
    source.edges.append(e)
    target.edges.append(e)
    return g

def CreateGraphFromInstance(instance):
    """Create graph with same properties and isomorphic to given instance, but with new vertex/edge IDs."""
    g = Graph()
    # Add vertices
    vertexId = 1
    vertexMapping = {}
    for vertex in instance.vertices:
        newVertex = Vertex(str(vertexId))
        newVertex.timestamp = vertex.timestamp
        newVertex.attributes = vertex.attributes
        g.vertices[newVertex.id] = newVertex
        vertexMapping[vertex.id] = newVertex
        vertexId += 1
    # Add edges
    edgeId = 1
    for edge in instance.edges:
        source = vertexMapping[edge.source.id]
        target = vertexMapping[edge.target.id]
        newEdge = Edge(str(edgeId), source, target, edge.directed)
        newEdge.timestamp = edge.timestamp
        newEdge.attributes = edge.attributes
        g.edges[newEdge.id] = newEdge
        source.edges.append(newEdge)
        target.edges.append(newEdge)
        edgeId += 1
    return g

    
