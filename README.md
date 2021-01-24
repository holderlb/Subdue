# Subdue Graph Miner

The Subdue graph miner discovers highly-compressing patterns in an input graph.  Compression is measured by the reduction in graph size after replacing each instance of the pattern with a single node. This version of Subdue can also find temporal patterns, i.e., the instances of the pattern also match in terms of the arrival order of the nodes and edges that comprise the pattern.

Starting with version 1.2, Subdue uses a polynomially-bounded, approximate graph isomorphism algorithm to improve efficiency while maintaining reasonable accuracy.

Subdue is designed to accept input graphs in the format produced by the [Graph Stream Generator](https://github.com/holderlb/graph-stream-generator).

Author: Dr. Larry Holder, School of Electrical Engineering and Computer Science, Washington State University, email: holder@wsu.edu.

Support: This material is based upon work supported by the National Science Foundation under Grant No. 1646640.

## Running Subdue

#### CLI
Subdue is run using the following command-line format (requires Python 3):

`python Subdue.py [options] <inputfile>`

The options, input file format and output are described below.

#### networkx
Alternatively, if you work with `networkx`, you can execute `Subdue.nx_subdue` directly on the graph. See function's
documentation for details. Simple usage is as follows:
```python
from Subdue import nx_subdue
out = nx_subdue(graph, **params)
```

## Options

The following options are available in Subdue.

`--beam <n>`

Number of patterns to retain after each expansion of previous patterns; based on their compression value. Default is 4.

`--iterations <n>`

Number of iterations of Subdue's discovery process. If more than 1, Subdue compresses the graph with the best pattern and then runs again using the compressed graph. If 0, then Subdue runs until no more compression (i.e., set to |E|). Default is 1.

`--limit <n>`

Number of patterns considered in each iteration of Subdue. A value of 0 implies |E|/2. Default is 0.

`--maxsize <n>`

Maximum size (#edges) of a pattern. A value of 0 implies |E|/2. Default is 0.

`--minsize <n>`

Minimum size (#edges) of a pattern. Default is 1.

`--numbest <n>`

Number of best patterns to report at end. Default is 3.

`--overlap <overlap_type>`

Controls how instances of a pattern may overlap. Possible overlap_type values are: none, vertex, edge. Overlap of "none" means no part of two instances of a pattern can overlap. Overlap of "vertex" means that any number of vertices can overlap, but no edges. Overlap of "edge" means that edges and vertices can overlap, but the two instances cannot be identical. Default is "none".

`--prune`

If enabled, Subdue removes any pattern whose value is worse than its parent pattern. Disabled by default.

`--temporal`

If enabled, Subdue discovers temporal patterns, i.e., patterns whose instances are not only isomorphic, but also match in terms of their vertex and edge arrival order. Disabled by default (i.e., static patterns that ignore timestamps).

`--valuebased`

If enabled, then all patterns with the top *beam* values are retained during the discovery process. Disabled by default.

`--writecompressed`

If enabled, Subdue writes the compressed graph after each iteration *i* to the file *outputFileName-compressed-i.json*, where *outputFileName* is the same as the input file name, but with *.json* removed if present. Disabled by default.

`--writeinstances`

If enabled, Subdue writes instances of the best pattern at iteration i as one graph to file *outputFileName-instances-i.json*. Disabled by default.

`--writepattern`

If enabled, Subdue writes the best pattern at iteration i to file *outputFileName-pattern-i.json*. Disabled by default.

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

Subdue outputs the top patterns according to their compression value along with their instances in the input graph. The file *output.txt* contains the output produced by Subdue on *inputgraph.json* using default options.

## Questions?

Contact: Dr. Larry Holder, School of Electrical Engineering and Computer Science, Washington State University, email: holder@wsu.edu.

