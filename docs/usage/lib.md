---
title: Library
icon: lucide/package
---
# Library

## Top level Functions

* [`model`](../reference/graphinate/index.md#graphinate.model) -
  Create a [`GraphModel`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel)

* [`build`](../reference/graphinate/index.md#graphinate.build) -
  Generate a [`GraphRepresentation`](../reference/index.md) from a [
  `GraphModel`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel)

* [`abuild`](../reference/graphinate/index.md#graphinate.abuild) -
  Asynchronously generate a [`GraphRepresentation`](../reference/index.md) from a [
  `GraphModel`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel) containing `async def` suppliers

## SDK

### Model

* [`graphinate.GraphModel`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel)

      The `GraphModel` Class which is used to declaratively register, Edge and/or Node data supplier functions.
      Using the [`GraphModel.node()`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel.node)
      and [`GraphModel.edge()`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel.edge) decorators,
      and compose models via `+` or [`GraphModel.merge()`](../reference/graphinate/modeling.md#graphinate.modeling.GraphModel.merge).

### Engine

* [`graphinate.engine.GraphEngine`](../reference/graphinate/engine.md#graphinate.engine.GraphEngine) -
  Decoupled traversal engine that dispatches [`NodeEvent`](../reference/graphinate/engine.md#graphinate.engine.NodeEvent) and [`EdgeEvent`](../reference/graphinate/engine.md#graphinate.engine.EdgeEvent) instances to [`GraphObserver`](../reference/graphinate/engine.md#graphinate.engine.GraphObserver) implementations via `run()` and `arun()`.

### Builders

* [`graphinate.builders.NetworkxBuilder`](../reference/graphinate/builders.md#graphinate.builders.NetworkxBuilder) -
  Generates a NetworkX Graph instance.

* [`graphinate.builders.D3Builder`](../reference/graphinate/builders.md#graphinate.builders.D3Builder) - Generates a D3
  Graph instance (i.e. a Dict).

* [`graphinate.builders.GraphQLBuilder`](../reference/graphinate/builders.md#graphinate.builders.GraphQLBuilder) - Generates
  a Strawberry GraphQL Schema instance (supports `SchemaMode.DYNAMIC` and `SchemaMode.STATIC`, as well as context-injected graphs).

* [`graphinate.builders.MermaidBuilder`](../reference/graphinate/builders.md#graphinate.builders.MermaidBuilder) - Generates
  a Mermaid Diagram
