# Introduction

## What is Graphinate?

Graphinate is a python library that aims to simplify the generation of Graph Data Structures from Data Sources.

It can help create an efficient retrieval pipeline from a given data source, while also enabling the developer to easily
map data payloads and hierarchies to a Graph.

In addition, there are several modes of output to enable examination of the Graph, and it's content.

Graphinate utilizes and builds upon the excellent [**_NetworkX_**](https://networkx.org/).

## What is a Graph?

“In a mathematician's terminology, a graph is a collection of points and lines connecting some (possibly empty) subset
of them. The points of a graph are most commonly known as graph vertices, but may also be called "nodes" or simply "
points." Similarly, the lines connecting the vertices of a graph are most commonly known as graph edges, but may also
be called "arcs" or "lines."”

&mdash; [https://mathworld.wolfram.com/Graph.html](https://mathworld.wolfram.com/Graph.html)

## What is Data?

“...data is a collection of discrete or continuous values that convey information, describing the quantity, quality,
fact, statistics, other basic units of meaning, or simply sequences of symbols that may be further interpreted
formally.”

&mdash; [https://en.wikipedia.org/wiki/Data](https://en.wikipedia.org/wiki/Data)

## A Graph as Data Structure

A Graph is a very useful data structure. They are the simplest data structure that is more the just simple collection of
entities. As such they can be used to model all data sources that have structure.

Let's start with a simple use case, The Social Network Graph.

## Defining a Graph

One can define a Graph in two general ways:

### Edge first

Generate a Graph by supplying a list of edges. The simplest definition of an edge will be a tuple of 2 values. Each
value represent a node (or vertex) in the graph. Additional attributes may be also added to the edge definition to
signify additional meaning.

In this case one defines the **edges explicitly** and the **nodes implicitly**.

Such graph is focused more on the _relationships_ or the _structure_ of the Graph than on the nodes themselves.

### Node first

Alternatively, one can first add nodes (vertices) to a graph without defining edges. Additional attributes may be added
to the node definition to signify additional meaning. Later on edge definitions are added to generate the relationships
between the nodes.

In this case **both nodes and the edges** are defines **explicitly**.

Such a graph has focus first on the nodes and later on the relationship between them.

## Graphinate - Hydrate a Graph from a Data Source