# Library

## Top level Functions


* `model` - Create a `GraphModel`

* `build` - Generate a Graph from a `GraphModel`

* `plot` - Generate a matplotlib plot

* `graphql` - Run a GraphQL Server

* `materialize` - Generate an output from a `GraphModel` instance.

      By default, the user will be prompted to choose the output format, using a popup GUI dialog.


## SDK

### Modeling

* `graphinate.GraphModel`

      Graphinate defines the `GraphModel` Class which can be used to declaratively register Edge and/or Node data
      supplier functions using the `GraphModel.node()` and `GraphMode.edge()` decorators.

* `graphinate.NodeModel` - TBD

### Builders

* `graphinate.builders.NetworkxBuilder` - Used to generate a NetworkX Graph instance.

* `graphinate.builders.D3Builder` - Used to generate a D3 Graph instance (i.e. a Dict).

* `graphinate.builders.GraphQLBuilder` - Used to generate a Strawberry GraphQL Schema instance

### Actualizers

> TBD

### Materializers

> TBD