import graphinate
import graphinate.modeling
import networkx as nx

N: int = 8


def polygonal_graph_model(number_of_sides: int = N):
    """
    Create a polygonal graph model.

    Args:
        number_of_sides (int): Number of sides in the polygon. Defaults to N.

    Returns:
        GraphModel: A graph model representing a polygonal graph.
    """

    # Define GraphModel
    graph_model = graphinate.model(name="Octagonal Graph")

    # Register edges supplier function
    @graph_model.edge()
    def edge():
        for i in range(number_of_sides - 1):
            yield {'source': i, 'target': i + 1}
        yield {'source': number_of_sides - 1, 'target': 0}

    return graph_model


model = polygonal_graph_model()

if __name__ == '__main__':
    use_materialize = True

    if use_materialize:
        # Materialize the GraphModel
        graphinate.materialize(
            model,
            builder=graphinate.builders.GraphQLBuilder,
            actualizer=graphinate.graphql
        )

    else:
        # Or

        # 1. Define Graph Builder
        builder = graphinate.builders.NetworkxBuilder(model=model)

        # Then
        # 2. Build the Graph object
        graph: nx.Graph = builder.build()

        # Then
        # 3. Option A - Output to console
        print(graph)

        # Or
        # 3. Option B - Output as a plot
        graphinate.materializers.plot(graph)
