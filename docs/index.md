# Graphinate. Data to Graphs.

<img style="width: 360px;" src="https://github.com/erivlis/graphinate/assets/9897520/dae41f9f-69e5-4eb5-a488-87ce7f51fa32" alt="Graphinate. Data to Graphs.">

## Meet Graphinate

**Graphinate** turns your data into Graphs. Effortlessly.

It is a Python library designed to streamline the pipeline from raw data to structured Graph representations. With Graphinate, you can easily map complex data hierarchies and payloads directly to nodes and edges, creating an efficient retrieval system.

Whether you need to visualize relationships, analyze structure, or serve data via an API, Graphinate provides the tools to bring your graph to life.

**Graphinate** uses and builds upon the excellent [**_NetworkX_**](https://networkx.org/).

## Library at a Glance

### 📐 The Architect (`graphinate.modeling`)
Define the blueprint of your graph by decorating simple functions that yield your data as nodes and edges.

### 🏗️ The Construction Crew (`graphinate.builders`)
Takes your graph blueprint and constructs various outputs, whether it's a queryable `NetworkX` object, a `Mermaid` diagram, or a `GraphQL` schema.

### 🎨 The Artists (`graphinate.renderers`)
A suite of tools to visualize your graphs, from `matplotlib` plots to interactive `Mermaid` diagrams.

### 📡 The Broadcaster (`graphinate.server`)
Instantly serve your graph data as an interactive `GraphQL` API, ready for consumption by web applications.

### ⌨️ The Command Center (`graphinate.cli`)
A handy command-line tool to manage and interact with your graph definitions without writing boilerplate code.
