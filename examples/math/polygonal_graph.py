import graphinate
import networkx as nx

N: int = 8

# Define GraphModel
graph_model = graphinate.GraphModel(name="Octagonal Graph")


# Register edges supplier function
@graph_model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# Materialize the GraphModel
graphinate.materialize(graph_model)

# Or

# 1. Define Graph Builder
builder = graphinate.builders.NetworkxBuilder(model=graph_model)

# Then
# 2. Build the Graph object
graph: nx.Graph = builder.build()

# Then
# 3. Option A - Output to console
print(graph)

# Or
# 3. Option B - Output as a plot
graphinate.materializers.plot(graph)
