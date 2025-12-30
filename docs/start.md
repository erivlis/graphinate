# Quick Start

**Graphinate** is designed to be used as a library first and foremost.
In addition, it has the following interfaces for ease of use: a CLI and a GraphQL API (using [_Strawberry GraphQL_
](https://strawberry.rocks/)).

## Install

**Graphinate** is available on PyPI.

=== "pip"

    ```shell
    pip install graphinate
    ```

    To install with server support:

    ```shell
    pip install graphinate[server]
    ```

=== "uv"

    ```shell
    uv add graphinate
    ```

    To install with server support:

    ```shell
    uv add graphinate --extra server
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

# 1. Define a GraphModel
# This model will hold all your graph's definitions, including how to generate nodes and edges.
graph_model: graphinate.GraphModel = graphinate.model(name='Octagonal Graph')


# 2. Define a function that provides the graph's edges
# The @graph_model.edge() decorator registers this function as the edge supplier.
# The function should yield a dictionary for each edge, specifying its 'source' and 'target'.
@graph_model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# 3. Build the graph with a NetworkX representation
# The NetworkxBuilder takes your graph model and constructs a NetworkX graph object.
builder = graphinate.builders.NetworkxBuilder(graph_model)
graph = builder.build()

# You can then visualize the graph using Matplotlib
# The plot function provides a quick way to see your graph.
graphinate.matplotlib.plot(graph, with_edge_labels=True)

# 4. Alternatively, create a Mermaid diagram for documentation
# The MermaidBuilder generates a string that can be used to create a Mermaid diagram.
builder = graphinate.builders.MermaidBuilder(graph_model)
diagram: str = builder.build()

# You can then generate Markdown or an HTML file to display the diagram.
mermaid_markdown: str = graphinate.mermaid.markdown(diagram)
mermaid_html: str = graphinate.mermaid.html(diagram, title=graph_model.name)

# 5. Or, expose your graph through a GraphQL API
# The GraphQLBuilder creates a Strawberry GraphQL schema.
builder = graphinate.builders.GraphQLBuilder(graph_model)
schema = builder.build()

# You can then serve this schema using a web server like Uvicorn.
graphinate.graphql.server(schema)
```

This example provides a glimpse into what **Graphinate** can do.
For more detailed guides and advanced features, be sure to check out the
[Tutorial](/tutorial) and the [Examples](/examples/code) sections.
