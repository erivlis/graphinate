# Quick Start

**Graphinate** is designed to be used as a library first and foremost.
In addition, it has several interfaces for ease of use: CLI and a GraphQL API (using [**_Strawberry GraphQL_
**](https://strawberry.rocks/)).

## Install

**Graphinate** is available on PyPI:

```shell
pip install graphinate
```

To install with server support

```shell
pip install graphinate[server]
```

**Graphinate** officially supports Python >= 3.10.

## Demo

```python title="Octagonal Graph"
import examples.math.materializers
import graphinate

N: int = 8

# Define a GraphModel
graph_model: graphinate.GraphModel = graphinate.model(name="Octagonal Graph")


# Register in the Graph Model the edges' supplier function
@graph_model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# Choose builder and handler
builder, handler = examples.math.materializers.Materializers.NetworkX_with_edge_labels.value

# Use the NetworkX Builder
builder = graphinate.builders.NetworkxBuilder(graph_model)

# build the NetworkX graph
graph = builder.build()

# plot the graph using matplotlib
graphinate.plot(graph, with_edge_labels=True)
```