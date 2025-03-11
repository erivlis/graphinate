# Library

## Top level Functions

* [`model`](/reference/graphinate/#graphinate.model) -
  Create a [`GraphModel`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel)

* [`build`](/reference/graphinate/#graphinate.build) -
  Generate a [`GraphRepresentation`](/ref) from a [
  `GraphModel`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel)

## SDK

### Model

* [`graphinate.GraphModel`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel)

      The `GraphModel` Class which is used to declaratively register, Edge and/or Node data supplier functions.
      Using the [`GraphModel.node()`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel.node)
      and [`GraphMode.edge()`](/reference/graphinate/modeling/#graphinate.modeling.GraphModel.edge) decorators.

### Builders

* [`graphinate.builders.NetworkxBuilder`](/reference/graphinate/builders/#graphinate.builders.NetworkxBuilder) -
  Generates a NetworkX Graph instance.

* [`graphinate.builders.D3Builder`](/reference/graphinate/builders/#graphinate.builders.D3Builder) - Generates a D3
  Graph instance (i.e. a Dict).

* [`graphinate.builders.GraphQLBuilder`](/reference/graphinate/builders/#graphinate.builders.GraphQLBuilder) - Generates
  a Strawberry GraphQL Schema instance

* [`graphinate.builders.MermaidBuilder`](/reference/graphinate/builders/#graphinate.builders.MermaidBuilder) - Generates
  a Mermaid Diagram