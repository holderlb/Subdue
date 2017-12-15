# Subdue Graph Miner

The Subdue graph miner discovers highly-compressing patterns in an input graph.  Compression is measured by the reduction in graph size after replacing each instance of the pattern with a single node. This version of Subdue can also find temporal patterns, i.e., the instances of the pattern also match in terms of the arrival order of the nodes and edges that comprise the pattern.

Author: Dr. Larry Holder, School of Electrical Engineering and Computer Science, Washington State University, email: holder@wsu.edu.

Support: This material is based upon work supported by the National Science Foundation under Grant No. 1646640.

## Running Subdue

You run Subdue using the following command-line format:

`python Subdue.py [options] <inputfile>`

The options, input file format and output are described below.

## Options

The following options are available in Subdue.

--beam

-- iterations

--limit

--maxsize

--minsize

--numsubs

--prune

--valuebased

--writecompressed

--writesub

--writeinsts

--temporal


## Input File

The input file represents a graph in JSON format. An example is in the file
*inputgraph.json*, and a visualization of this graph is in *inputgraph.png*.
The input graph contains a JSON array of vertices and edges, as described below.

### Vertex

A vertex is a JSON object with name "vertex" and whose value is a JSON object with the following properties.

* **id**: A string identifier that uniquely identifies this vertex.
* **attributes**: A JSON object of name/value pairs, where both the name and value are strings. For two vertices to match, all of their attributes must match.
* **timestamp**: An integer value (as a string) representing the time at which this vertex first appeared in the graph. Timestamps are only used if Subdue is run with the *--temporal* option.

### Edge

An edge is a JSON object with name "edge" and whose value is a JSON
object with the following properties.

* **id**: A string identifier that uniquely identifies this edge.
* **source**: Vertex identifier string for the edge's source vertex.
* **target**: Vertex identifier string for the edge's target vertex.
* **directed**: Whether the edge is directed from source to target ("true"), or undirected ("false").
* **attributes**: A JSON object of name/value pairs, where both the name and value are strings. For two edges to match, all of their attributes must match.
* **timestamp**: An integer value (as a string) representing the time at which this edge first appeared in the graph. Timestamps are only used if Subdue is run with the *--temporal* option.

## Output


## Questions?

Contact: Dr. Larry Holder, School of Electrical Engineering and Computer Science, Washington State University, email: holder@wsu.edu.

