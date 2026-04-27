# Library

## Top level Functions

* [`model`](../reference/graphinate/index.md#graphinate.model) -
  Create a [`GraphModel`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel)

* [`build`](../reference/graphinate/index.md#graphinate.build) -
  Generate a [`GraphRepresentation`](../reference/index.md) from a [
  `GraphModel`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel)

## SDK

### Model

* [`graphinate.GraphModel`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel)

      The `GraphModel` Class which is used to declaratively register, Edge and/or Node data supplier functions.
      Using the [`GraphModel.node()`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel.node)
      and [`GraphMode.edge()`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel.edge) decorators.

### Builders

* [`graphinate.builders.NetworkxBuilder`](../reference/graphinate/builders/index.md#graphinate.builders.NetworkxBuilder) -
  Generates a NetworkX Graph instance.

* [`graphinate.builders.D3Builder`](../reference/graphinate/builders/index.md#graphinate.builders.D3Builder) - Generates a D3
  Graph instance (i.e. a Dict).

* [`graphinate.builders.GraphQLBuilder`](../reference/graphinate/builders/index.md#graphinate.builders.GraphQLBuilder) - Generates
  a Strawberry GraphQL Schema instance

* [`graphinate.builders.MermaidBuilder`](../reference/graphinate/builders/index.md#graphinate.builders.MermaidBuilder) - Generates
  a Mermaid Diagram
