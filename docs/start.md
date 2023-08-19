
## Quick Start

Graphinate is designed to be used as library first and foremost. In addition, it has several interfaces for ease of
use: CLI, TUI (using [Textual]) and a GraphQL API (using [**_Strawberry GraphQL_**](https://strawberry.rocks/)).

### GraphModel

Graphinate defines the _**GraphModel**_ Class which can be used to declaratively register Edge and/or Node data
supplier functions by using decorators.

### Materialize

Graphinate supplies quick materialize function to output the GraphModel.

### Sample Code

```python
import graphinate

# Define GraphModel
model = graphinate.GraphModel(name= "Octagonal Graph")

# Register edges supplier function
N: int = 8


@model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# Materialize the GraphModel
graphinate.materialize(model)
```
