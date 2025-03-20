import operator

import graphs
import networkx as nx
from materializers import Materializers, materialize

import graphinate


def model(items: list[tuple[str, nx.Graph]]) -> graphinate.GraphModel:
    """
    Generate a graph model based on the provided iterable of graphs.
    The function creates a graph model named 'Graph Atlas' using the 'graphinate' library.
    It then combines all the graphs from the input iterable into a single disjoint union graph using NetworkX library.
    The function defines edges for the combined graph by iterating over all edges in the disjoint union graph and
    yielding dictionaries with 'source' and 'target' keys representing the edge connections.
    Finally, the function yields the created graph model containing the combined graph with defined edges.

    Args:
        items: A list containing graphs to be combined into a single graph model.

    Yields:
        GraphModel: A graph model containing the combined graph with defined edges.
    """

    def items_iter(recs):
        for name, g in recs:
            print(name)
            yield g

    g = nx.disjoint_union_all(items_iter(items)) if len(items) > 1 else items[0][1]

    graph_model = graphinate.model('Graph Atlas')

    @graph_model.node(operator.itemgetter(1),
                      key=operator.itemgetter(0),
                      value=operator.itemgetter(0))
    def nodes():
        yield from g.nodes(data='type')

    @graph_model.edge(operator.itemgetter('type'))
    def edge():
        yield from ({'source': e[0], 'target': e[1], **e[2]} for e in g.edges.data())

    return graph_model


if __name__ == '__main__':
    from gui import ListboxChooser, RadiobuttonChooser

    graph_atlas = graphs.atlas()

    listbox_chooser = ListboxChooser('Choose Graph/s', graph_atlas)
    choices = list(listbox_chooser.get_choices())
    model = model(choices)

    # or
    # model(graph_atlas.values())

    radiobutton_chooser = RadiobuttonChooser('Choose Materializer',
                                             options={m.name: m.value for m in Materializers},
                                             default=(None, None))
    result = radiobutton_chooser.get_choice()
    builder, handler = result[1]
    materialize(model, builder=builder, builder_output_handler=handler)
