---
title: Introduction
icon: lucide/book-open
---
# Introduction

## Why?

### Why Graphs?

A Graph is a powerful data structure, which can be used to model a wide range of problems.
Graphs are used in many fields, such as computer science, mathematics, physics, biology, social sciences and more.

### Why Graphinate?

Usually the creation of a Graph is a tedious and error-prone process.
It requires a lot of boilerplate code to transform data into a Graph.
This process can be automated and simplified. This is where **Graphinate** comes in.

## What?

### What is a Graph?

!!! quote

    “In a mathematician's terminology, a graph is a collection of points and lines connecting some (possibly empty) subset
    of them.
    The points of a graph are most commonly known as graph *vertices*, but may also be called *nodes* or *points*.
    Similarly, the lines connecting the vertices of a graph are most commonly known as graph *edges*, but may also
    be called *arcs* or *lines*.”

    &mdash; [https://mathworld.wolfram.com/Graph.html](https://mathworld.wolfram.com/Graph.html)

### What is Data?

!!! quote

    “...data is a collection of discrete or continuous values that convey information, describing the quantity, quality,
    fact, statistics, other basic units of meaning, or simply sequences of symbols that may be further interpreted
    formally.”
   
    &mdash; [https://en.wikipedia.org/wiki/Data](https://en.wikipedia.org/wiki/Data)

### What is Graphinate?

**Graphinate** is a Python library that automates the generation and population of Graph Data Structures from arbitrary
Data Sources.

It provides a declarative, event-driven retrieval and hydration pipeline—supporting synchronous and asynchronous data
suppliers (`async def`), modular model composition (`model1 + model2`), and streaming graph traversal via the
`GraphEngine`.

Once modeled, graphs can be built into multiple representations (including [**_NetworkX_**](https://networkx.org/),
D3, Mermaid, or GraphQL schemas) and visualized or served through interactive APIs and embedded, offline 3D WebGL
viewers.

## How?

### A Graph as a Data Structure

A Graph can be a useful data structure.
It is, perhaps, the simplest data structure, which is a "bit more" than just a simple collection of "things".
As such, it can be used to model any data source that has structure.

### Graph Elements

A Graph consists of two types of elements:

#### Nodes

A Graph Node can be any Python Hashable object. Usually it will be a primitive type such as an integer or a string,
in particular when the node in itself has no specific meaning.

One can also add attributes to the node to describe additional information. This information can be anything.
Often attributes are used to store scalar dimensions (e.g., weight, area, width, age, etc.)
or stylistic information (e.g., color, size, shape, label, etc.).

Nodes are usually visualized as circles or points.

#### Edges

A Graph Edge is a pair of two node values. It can also have additional attributes in the same vain as a Graph Node.

Edges are usually visualized as lines connecting two nodes.

### Defining a Graph

One can define a Graph in two general ways:

#### Edge First

The most straightforward way to generate a Graph is to supply a list of edges. The simplest definition of an edge is a
pair of two values. Each value represents a node (or vertex) in the graph. Attributes may be added to the edge
definition to convey additional characteristics, such as weight, direction, etc.

In this case, one defines the **edges explicitly** and the **nodes implicitly**.

Such a graph is focused more on the _relationships_ between nodes, or the _structure_ of the graph,
than on the nodes themselves.

#### Node First

Alternatively, one can first add nodes (vertices) to a graph without defining edges. Attributes may be added
to the node definitions to convey additional characteristics. After that, edge definitions are added to generate the
relationships between the nodes.

In this case, **both nodes and the edges** are defined **explicitly**.

Such a graph may have a focus primarily on the nodes, and then only if needed on the relationship between them.

### Graphinate

Graphinate helps to generate graphs from data sources ("Hydrate" a Graph Model from a Data Source.)
It supports both *Edge First* and *Node First* creation scenarios.

This is achieved the following way:

#### Source

First, data sources are represented as an `Iterable` or `AsyncIterable` of items.
Sources supply the data items used to generate graph nodes and edges.
It is recommended to use a generator (`yield` or `async yield`) as the supplier so data can be lazily streamed on demand.
A source can be anything from a simple Python list or dictionary generator to a database query, file stream, or remote API call.

#### Model

Graphinate introduces the concept of a `GraphModel`.
A `GraphModel` embodies declarative rules defining how data source items map into Graph elements (nodes or edges).
Sources are registered using `@model.node()` and `@model.edge()` decorators, which extract keys, labels, and attributes.
Models are modular and composable—multiple models can be combined seamlessly using `+` or `GraphModel.merge()`.

#### Engine

The `GraphEngine` drives graph traversal. It coordinates the execution lifecycle—invoking suppliers, streaming elements,
and emitting lifecycle events (`on_start`, `on_node`, `on_edge`, `on_finish`) to registered observers.
The engine supports both synchronous execution (`run()`) and asynchronous execution (`arun()`), enabling non-blocking pipelines.

#### Builders

A `GraphModel` is transformed into concrete output representations using `GraphBuilder` classes.
Builders act as engine observers that accumulate or structure graph data during traversal.
Graphinate provides built-in builders for:

- **NetworkX**: In-memory `nx.Graph` instances for topological and structural analysis.
- **D3**: Node-link dictionaries formatted for D3.js force-directed visualizations.
- **Mermaid**: Markdown diagram specifications for documentation.
- **GraphQL**: Executable Strawberry GraphQL schemas for querying nodes and relationships (supporting dynamic schema synthesis or static typed models).

Builders can be executed synchronously (`builder.build()`) or asynchronously (`await graphinate.abuild(BuilderClass, model)`).

#### Renderers & Broadcaster

Finally, built representations can be rendered or served:

- **Renderers**: Visualize graphs directly via Matplotlib plots or export HTML and Markdown Mermaid diagrams.
- **Broadcaster**: Serve GraphQL APIs using Uvicorn/FastAPI with an embedded, 100% offline 3D WebGL graph viewer requiring zero external CDNs.
