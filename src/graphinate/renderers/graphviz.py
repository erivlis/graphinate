import networkx as nx
from graphviz import Digraph, Graph


def to_graphviz(graph: nx.Graph, with_node_labels: bool = True, with_edge_labels: bool = False):
    """
    Converts a networkx graph to a graphviz graph.

    Args:
        graph (nx.Graph): The input graph to be converted.
        with_node_labels (bool): Whether to include node labels. Default is True.
        with_edge_labels (bool): Whether to include edge labels. Default is False.

    Returns:
        graphviz.Graph or graphviz.Digraph: The converted graphviz graph.
    """
    viz_graph = Digraph(graph.name) if graph.is_directed() else Graph(graph.name)

    for node, data in graph.nodes(data=True):
        label = data.get('label', str(node)) if with_node_labels else str(node)
        viz_graph.node(str(node), label)

    for source, target, data in graph.edges(data=True):
        if with_edge_labels:
            label = data.get('label', '')
            viz_graph.edge(str(source), str(target), label=label)
        else:
            viz_graph.edge(str(source), str(target))

    return viz_graph

def render(
    graph: nx.Graph,
    output_path: str,
    format: str = 'png',
    with_node_labels: bool = True,
    with_edge_labels: bool = False,
    view: bool = False
):
    """
    Renders the given networkx graph to a file using graphviz.

    Args:
        graph (nx.Graph): The input graph to be rendered.
        output_path (str): The path to the output file (without extension).
        format (str): The output format (e.g., 'png', 'svg', 'pdf'). Default is 'png'.
        with_node_labels (bool): Whether to include node labels. Default is True.
        with_edge_labels (bool): Whether to include edge labels. Default is False.
        view (bool): Whether to open the rendered file with the default viewer. Default is False.
    """
    viz_graph = to_graphviz(graph, with_node_labels, with_edge_labels)
    viz_graph.render(output_path, format=format, view=view, cleanup=True)
