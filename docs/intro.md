# Introduction

## What?

### What is Graphinate?

**Graphinate** is a python library that aims to simplify the generation of Graph Data Structures from Data Sources.

It can help create an efficient retrieval pipeline from a given data source, while also enabling the developer to map
data payloads and hierarchies to a Graph.

In addition, there are several modes of output to enable examination of the Graph and its content.

**Graphinate** utilizes and builds upon the excellent [**_NetworkX_**](https://networkx.org/).

### What is a Graph?

“In a mathematician's terminology, a graph is a collection of points and lines connecting some (possibly empty) subset
of them.
The points of a graph are most commonly known as graph *vertices*, but may also be called *nodes* or *points*.
Similarly, the lines connecting the vertices of a graph are most commonly known as graph *edges*, but may also
be called *arcs* or *lines*.”

&mdash; [https://mathworld.wolfram.com/Graph.html](https://mathworld.wolfram.com/Graph.html)

### What is Data?

“...data is a collection of discrete or continuous values that convey information, describing the quantity, quality,
fact, statistics, other basic units of meaning, or simply sequences of symbols that may be further interpreted
formally.”

&mdash; [https://en.wikipedia.org/wiki/Data](https://en.wikipedia.org/wiki/Data)

## How?

### A Graph as a Data Structure

A Graph is a quite useful data structure.
It is perhaps the simplest data structure, that is a bit more than just a
simple collection of "things".
As such, it can be used to model all data sources that have structure.

### Graph Elements

A Graph consists of two types of elements:

#### Nodes

A Graph Node can be any Python Hashable object. Usually it will be a primitive type such as an integer or a string,
in particular when the node in itself has no special meaning.
One can also add attributes to the node to describe additional information.
This information can include anything. Often they are used to store scalar dimensions (e.g., weight, area, width, age etc.)
or stylistic information (e.g., color, size, shape, label etc.).  

#### Edges

A Graph Edge is a tuple of two node values. It can also have additional attributes in the same vain as a Graph Node. 

### Defining a Graph

One can define a Graph in two general ways:

#### Edge First

The most straight forward way to generate a Graph is to supply a list of edges. The simplest definition of an edge is a
tuple of two values. Each value represents a node (or vertex) in the graph. Attributes may be added to the edge
definition to convey additional characteristics.

In this case, one defines the **edges explicitly** and the **nodes implicitly**.

Such a graph is focused more on the _relationships_ between nodes or the _structure_ of the graph than on the nodes themselves.

#### Node First

Alternatively, one can first add nodes (vertices) to a graph without defining edges. Attributes may be added
to the node definitions to convey additional characteristics. After that, edge definitions are added to generate the
relationships between the nodes.

In this case, **both nodes and the edges** are defined **explicitly**.

Such a graph has focus, first on the nodes, and then on the relationship between them.

### Graphinate 

"Hydrate" a Graph from a Data Source.
Using Graphinate enables generating graphs from data sources.
It supports both *Edge First* and *Node First* creation scenarios.

This is achieved following these steps: 

#### Source 

It is required to represent the Data sources as an Iterable of items that will be transformed to graph edges
and/or nodes.
It is recommended to use Generators as the items Iterables.

#### Model

Using Graphinate GraphMode decorators, we can define how to transform the items supplied by the data source generators,
to graph elements.

#### Build
A Graph Model can be used to generate an actual instance of a Graph.
It is achieved by using a GraphBuilder to both retrieve the data and assemble the Graph. 
Several formats are available.

#### Materialize

Finally, we can use the builders to Materialize the graph in several ways that support different use cases 
(i.e., visualizing, querying, reporting, etc.) 
