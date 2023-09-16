# Quick Start

Graphinate is designed to be used as library first and foremost. In addition, it has several interfaces for ease of
use: CLI and a GraphQL API (using [**_Strawberry GraphQL_**](https://strawberry.rocks/)).

## GraphModel

Graphinate defines the _**GraphModel**_ Class which can be used to declaratively register Edge and/or Node data
supplier functions by using decorators.

## Materialize

Graphinate supplies quick materialize function to output the GraphModel.

## Sample Code

```python
import graphinate

N: int = 8

# Define a GraphModel
graph_model = graphinate.GraphModel(name="Octagonal Graph")


# Register in the Graph Model the edges supplier function
@graph_model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# Materialize the GraphModel
graphinate.materialize(graph_model)
```