# Quick Start

**Graphinate** is designed to be used as a library first and foremost.
In addition, it has the following interfaces for ease of use: a CLI and a GraphQL API (using [_Strawberry GraphQL_
](https://strawberry.rocks/)).

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

The following code snippet shows basic simple usage of **Graphinate**.
It demonstrates how to wire a simple source function to a graph model, build graph representation of several types, and
render them. You can check the [Tutorial](/tutorial) for an in-depth step-by-step walkthrough, and
the [Examples](/examples/code) section for additional more complex use cases.

```python title="Octagonal Graph"
import graphinate

N: int = 8

# First Define a GraphModel instance.
# It will be used to hold the graph definitions
graph_model: graphinate.GraphModel = graphinate.model(name="Octagonal Graph")


# Register in the Graph Model the edges' supplier generator function
@graph_model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# Use the NetworkX Builder
builder = graphinate.builders.NetworkxBuilder(graph_model)

# build the NetworkX GraphRepresentation
# the output in this case is a nx.Graph instance
graph = builder.build()

# this supplied plot method uses matplotlib to display the graph
graphinate.matplotlib.plot(graph, with_edge_labels=True)

# or use the Mermaid Builder
builder = graphinate.builders.MermaidBuilder(graph_model)

# to create a Mermaid diagram
diagram: str = builder.build()

# and get Markdown or single page HTML to display it
mermaid_markdown: str = graphinate.mermaid.markdown(diagram)
mermaid_html: str = graphinate.mermaid.html(diagram, title=graph_model.name)

# or use the GraphQL Builder
builder = graphinate.builders.GraphQLBuilder(graph_model)

# to create a Strawberry GraphQL schema
schema = builder.build()

# and serve it using Uvicorn web server
graphinate.graphql.server(schema)
```