# Introduction

## Why?

### Why Graphs?

A Graph is a powerful data structure, that can be used to model a wide range of problems.
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

**Graphinate** is a python library that helps generate and populate Graph Data Structures from Data Sources.

It can help create an efficient retrieval pipeline from a given data source, while also enabling the developer to map
data payloads and hierarchies to a Graph.

There are several modes of building and rendering to facilitate examination of the Graph and its content.

**Graphinate** uses and is built upon the excellent [**_NetworkX_**](https://networkx.org/).

## How?

### A Graph as a Data Structure

A Graph can be a useful data structure.
It is, perhaps, the simplest data structure, that is a "bit more" than just a simple collection of "things".
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

First, it is required to represent the data sources, as an `Iterable` of items.
It will be supply the data items that will be used to create the graph edges and/or nodes.
It is recommended to use a `Generator`  as the items Iterable. This way, the data source can be
lazily-loaded.
Such an `Iterable` or `Generator` can be, anything from a simple list of dictionaries, to a complex database query.

#### Model

Graphinate introduces the concept of a `GraphModel`.
A GraphModel embodies a set of rules which define how to use a data source item in creating a Graph element (i.e.,
either a node or an edges). The `GraphModel` registers the sources using `GraphModel.node` and `GraphModel.edge`
decorators. These decorators define how to extract both mandatory and optional aspects of information, which then are
used to generate each Graph element.

#### Builders

A `GraphModel` can be used to generate an actual instance of a `GraphRepresentation`.
Such a `GraphRepresentation` will contain the actual Graph data structure, populated with the data items obtained from
the source.
Graphinate provides several `GraphBuilder` classes that can be used to build the `GraphRepresentation` from
a `GraphModel`. The actual nature of the `GraphRepresentation` will depend on the `GraphBuilder` used.

#### Renderers

Finally, we can render a builder's output `GraphRepresentation`. The Renderers chosen depends on the actual type of the
`GraphRepresentaion` and the desired rendering output format. Graphinate provides several Renderer classes that can be
used for different use cases such as visualizing, querying, reporting, etc.
