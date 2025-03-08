# Library

## Top level Functions

* [`model`](/reference/graphinate/#graphinate.model) -
  Create a [`GraphModel`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel)

* [`build`](/reference/graphinate/#graphinate.build) -
  Generate a Graph from a [`GraphModel`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel)

* [`plot`](/reference/graphinate/#graphinate.plot) - Generate a matplotlib plot

* [`graphql`](/reference/graphinate/#graphinate.graphql) - Run a GraphQL Server

* [`materialize`](/reference/graphinate/#graphinate.materialize) -
  Generate an output from a [`GraphModel`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel) instance.
  By default, the user will be prompted to choose the output format, using a popup GUI dialog box.

## SDK

### Model

* [`graphinate.GraphModel`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel)

      The `GraphModel` Class which is used to declaratively register, Edge and/or Node data supplier functions.
      Using the [`GraphModel.node()`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel.node)
      and [`GraphMode.edge()`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel.edge) decorators.

* [`graphinate.NodeModel`](/reference/graphinate/modeling/#graphinate.modeling.NodeModel) - TBD

### Build

* [`graphinate.builders.NetworkxBuilder`](/reference/graphinate/builders/#graphinate.builders.NetworkxBuilder) -
  Generates a NetworkX Graph instance.

* [`graphinate.builders.D3Builder`](/reference/graphinate/builders/#graphinate.builders.D3Builder) - Generates a D3
  Graph instance (i.e. a Dict).

* [`graphinate.builders.GraphQLBuilder`](/reference/graphinate/builders/#graphinate.builders.GraphQLBuilder) - Generates
  a Strawberry GraphQL Schema instance

