import graphinate
import networkx as nx

N: int = 8


def get_graph_model(number_of_sides: int = N):
    # Define GraphModel
    graph_model = graphinate.GraphModel(name="Octagonal Graph")

    # Register edges supplier function
    @graph_model.edge()
    def edge():
        for i in range(number_of_sides):
            yield {'source': i, 'target': i + 1}
        yield {'source': number_of_sides, 'target': 0}

    return graph_model


model = get_graph_model()

if __name__ == '__main__':
    use_materialize = True

    if use_materialize:
        # Materialize the GraphModel
        graphinate.materialize(model)
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
