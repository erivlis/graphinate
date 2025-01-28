from collections.abc import Iterable

import graphs
import networkx as nx

import graphinate
from graphinate.materializers import Materializers


def model(iterable: Iterable[nx.Graph]) -> graphinate.GraphModel:
    """
    Generate a graph model based on the provided iterable of graphs.
    The function creates a graph model named 'Graph Atlas' using the 'graphinate' library.
    It then combines all the graphs from the input iterable into a single disjoint union graph using NetworkX library.
    The function defines edges for the combined graph by iterating over all edges in the disjoint union graph and
    yielding dictionaries with 'source' and 'target' keys representing the edge connections.
    Finally, the function yields the created graph model containing the combined graph with defined edges.

    Args:
        iterable: An iterable containing graphs to be combined into a single graph model.

    Yields:
        GraphModel: A graph model containing the combined graph with defined edges.
    """

    graph_model = graphinate.model('Graph Atlas')

    @graph_model.edge()
    def edge():
        for e in nx.disjoint_union_all(g for _, g in iterable).edges:
            yield {'source': e[0], 'target': e[1]}

    return graph_model


if __name__ == '__main__':
    from gui import listbox_chooser, radiobutton_chooser

    graph_atlas = graphs.atlas()

    choices = listbox_chooser('Choose Graph', graph_atlas)

    model = model(choices)

    # or
    # model(graph_atlas.values())

    result = radiobutton_chooser('Choose Materializer',
                                 options={m.name: m.value for m in Materializers},
                                 default=(None, None))
    builder, handler = result[1]

    graphinate.materialize(model, builder=builder, builder_output_handler=handler)
