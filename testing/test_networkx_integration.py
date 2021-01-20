import os
import subprocess
import json
import re
import contextlib
import io
import sys
import networkx as nx

sys.path.append('../src')
import Parameters
from Subdue import ReadGraph, Subdue, nx_subdue

subdue_example_path = 'inputgraph.json'
tolerance_pct = 0.1  # mainly due to non-deterministic nature of the algorithm


def subdue_json_to_undirected_nx_graph(subdue_json_path):
    """WARNING: ignores directed edges and timestamp on purpose"""

    with open(subdue_json_path, 'r') as subdue_json_file:
        subdue_format = json.load(subdue_json_file)

    graph = nx.Graph()
    for vertex_or_edge in subdue_format:
        if list(vertex_or_edge.keys()) == ['vertex']:
            node_attributes_loop = vertex_or_edge['vertex']['attributes']
            graph.add_node(
                vertex_or_edge['vertex']['id'],
                **node_attributes_loop,
            )
        elif list(vertex_or_edge.keys()) == ['edge']:
            edge_attributes_loop = vertex_or_edge['edge']['attributes']
            graph.add_edge(
                u_of_edge=vertex_or_edge['edge']['source'],
                v_of_edge=vertex_or_edge['edge']['target'],
                **edge_attributes_loop,
            )
        else:
            raise ValueError('Invalid entry type')

    return graph


def main_with_path(file_path):
    """
    Imitates the cli call to subdue with default parameters and a `file_path`
    """
    parameters = Parameters.Parameters()
    # parameters.set_parameters(sys.argv)
    graph = ReadGraph(file_path)
    # outputFileName = parameters.outputFileName + ".dot"
    # graph.write_to_dot(outputFileName)
    parameters.set_defaults_for_graph(graph)
    Subdue(parameters, graph)


def unify_output_text(text):
    text = re.sub(r'Elapsed time = [0-9]*.[0-9]*', 'Elapsed time = REMOVED', text)
    text = re.sub(r'timestamp=[0-9]', 'timestamp=0', text)
    text = re.sub(r'timestamp=0[0-9]', 'timestamp=0', text)
    text = re.sub('edge \"[0-9]*\"', 'edge', text)
    text = re.sub('edge \"[0-9]*-[0-9]*\"', 'edge', text)
    return text


# normal run
capture_prints = io.StringIO()
with contextlib.redirect_stdout(capture_prints):
    main_with_path(subdue_example_path)
prints_main = capture_prints.getvalue()


# use networkx graph as an input
subdue_example_graph = subdue_json_to_undirected_nx_graph(subdue_example_path)
capture_prints = io.StringIO()
with contextlib.redirect_stdout(capture_prints):
    nx_subdue(graph=subdue_example_graph, verbose=True)
prints_nx_subdue = capture_prints.getvalue()


# compare
prints_main = unify_output_text(prints_main)
prints_nx_subdue = unify_output_text(prints_nx_subdue)

assert (
    (
        len(set(prints_nx_subdue.split('\n')) - set(prints_main.split('\n')))
        +
        len(set(prints_main.split('\n')) - set(prints_nx_subdue.split('\n')))
    )
    /
    len(prints_main.split('\n'))
) < tolerance_pct
