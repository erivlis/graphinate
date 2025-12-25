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

## Modeling Concepts

### Dependency Injection and Parameter Naming

When defining node generators using `@model.node`, you can request context from parent nodes by adding arguments to your generator function.

**Strict Naming Convention:**
To receive the ID of a parent node, your argument name must follow this pattern: `{node_type}_id`.

For example, if you have a node type `user`, a child node generator can request `user_id`.

```python
@model.node(parent_type='user')
def get_posts(user_id):
    # user_id is automatically injected
    ...
```

**Note:** Arbitrary arguments are not currently supported. All arguments must match a registered node type followed by `_id`.

### Examples

See the following examples for practical usage of this pattern:

* [GitHub Repositories Example](../examples/github.md#repositories) - Demonstrates a deep hierarchy (`user` -> `repository` -> `commit` -> `file`) using dependency injection.
