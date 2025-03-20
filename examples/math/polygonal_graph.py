import networkx as nx

import graphinate

# import graphinate.modeling
from graphinate import GraphModel


def polygonal_graph_edges(edges_count: int):
    for i in range(1, edges_count):
        yield {'source': i, 'target': i + 1}
    yield {'source': edges_count, 'target': 1}


def polygonal_graph_model(name: str, number_of_sides: int) -> graphinate.GraphModel:
    """
    Create a polygonal graph model.

    Args:
        name (str): The Graph's name.
        number_of_sides (int): Number of sides in the polygon.

    Returns:
        GraphModel: A graph model representing a polygonal graph.
    """

    # Define GraphModel
    graph_model: GraphModel = graphinate.model(name)

    # Register edges supplier function
    @graph_model.edge()
    def edge():
        yield from polygonal_graph_edges(number_of_sides)

    return graph_model

# instantiated here to be used to cli serving
model = polygonal_graph_model("Octagonal Graph", 8)

if __name__ == '__main__':

    # 1. Define Graph Builder
    builder = graphinate.builders.NetworkxBuilder(model)

    # Then
    # 2. Build the Graph object
    graph: nx.Graph = builder.build()

    # Then
    # 3. Option A - Output to console
    print(graph)

    # Or
    # 3. Option B - Output as a plot
    graphinate.renderers.matplotlib.plot(graph)

    # Alternatively,
    # 4. Define a GraphQL Builder
    builder = graphinate.builders.GraphQLBuilder(model)

    schema = builder.build()

    graphinate.graphql.server(schema, port=9077)
