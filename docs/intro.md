# Introduction

## Why?

### Why Graphs?

Graphs are a powerful data structure that can be used to model a wide range of problems.
They are used in many fields, such as computer science, mathematics, physics, biology, and social sciences.

### Why Graphinate?

Usually the creation phase of a Graph is a tedious and error-prone process.
It requires a lot of boilerplate code to transform data into a Graph.
This process can be automated and simplified. This is where **Graphinate** comes in.

## What?

### What is Graphinate?

**Graphinate** is a python library that can be used to generate Graph Data Structures from Data Sources.

It can help create an efficient retrieval pipeline from a given data source, while also enabling the developer to map
data payloads and hierarchies to a Graph.

In addition, there are several modes of output to enable examination of the Graph and its content.

**Graphinate** uses and is built upon the excellent [**_NetworkX_**](https://networkx.org/).

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

Graphinate helps to generate graphs from data sources ("Hydrate" a Graph from a Data Source.)
It supports both *Edge First* and *Node First* creation scenarios.

This is achieved the following way:

#### Source

It is required to represent the data sources, as an Iterable of items that will be transformed, to graph edges
and/or nodes.
It is recommended to use Generators as the items Iterables. This way, the data source can be lazy-loaded.
The Iterables or Generators can be anything, from a simple list of dictionaries to a complex database query.

#### Model

Graphinate introduces the concept of a Graph Model.
A Graph Model is a set of rules, that define how to transform the data source item into Graph elements (i.e. nodes and
edges). The GraphModel registers the sources using node and edge decorators.

#### Build

A Graph Model can be used to generate an actual instance of a Graph that contains the transformed source data.
Graphinate provides several GraphBuilder classes, that can be used to build the Graph from the Graph Model.

#### Materialize

Finally, we can use the builders to Materialize the graph in several ways that support different use cases
(i.e., visualizing, querying, reporting, etc.).
