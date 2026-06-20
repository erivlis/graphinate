---
name: graphinate
description: >
  Use this skill to turn data into graphs. Activate when the user wants to
  understand relationships, dependencies, or structure within their data,
  even if they don't explicitly mention "graph". This is ideal for tasks
  involving data lineage, code analysis, or dependency mapping.
---

# Skill: Graphinate - Data to Graphs

## 1. Objective

To use the `graphinate` library to "hydrate" a Graph Model from a data source, streamlining the pipeline from raw data
to a structured graph representation.

## 2. Core Concepts & Personas

Graphinate simplifies the creation of graphs by assigning clear roles to its components:

- **The Architect (`graphinate.modeling`)**: You define the *blueprint* of your graph using `@model.node` and
  `@model.edge` decorators on simple generator functions.
- **The Construction Crew (`graphinate.builders`)**: They take your blueprint and construct various outputs, like a
  `NetworkX` object or a `GraphQL` schema.
- **The Artists (`graphinate.renderers`)**: They visualize your graph in different formats, such as `matplotlib` plots
  or `Mermaid` diagrams.

## 3. Key Patterns for "The Architect"

You can define a graph in two main ways:

### Pattern 1: "Edge First" (Implicit Nodes)

This approach focuses on relationships and is the most straightforward way to generate a graph. Nodes are created
implicitly from the edges you define.

```python
import graphinate

model = graphinate.GraphModel(name="Edge-First Example")


# The nodes 'package-a', 'package-b', etc. are created automatically.
@model.edge()
def dependency():
    yield {'source': 'package-a', 'target': 'package-b'}
    yield {'source': 'package-a', 'target': 'package-c'}
```

### Pattern 2: "Node First" (Explicit Nodes & Attributes)

For more detailed graphs, define nodes explicitly. This is necessary when you need to attach specific attributes to
them. You can use functions (extractors) to dynamically determine node properties from your data.

- **`type_`**: A function that returns the node's type.
- **`key`**: A function that returns a unique identifier for the node.
- **`label`**: A function that returns the display label for the node.

```python
import graphinate
import operator

model = graphinate.GraphModel(name="Node-First Example")


def get_source_code_items():
    yield {'commit_sha': 'abc', 'summary': 'Fix bug', 'type': 'commit'}
    yield {'file_path': 'src/main.py', 'type': 'file'}


# A single generator can produce multiple types of nodes.
# The first argument to @model.node is the extractor for the node's type.
@model.node(operator.itemgetter('type'),
            key=lambda item: item.get('commit_sha') or item.get('file_path'),
            label=lambda item: item.get('summary') or item.get('file_path'))
def source_code():
    yield from get_source_code_items()
```

## 4. Protocols for "The Construction Crew" and "The Artists"

Once you have a `model`, you use a **Builder** to construct a graph object, and a **Renderer** to visualize it.

```python
import graphinate
import networkx as nx

# Let's assume 'model' is a GraphModel object from the patterns above.

# 1. The Construction Crew builds the graph object.
builder = graphinate.builders.NetworkxBuilder(model)
graph: nx.Graph = builder.build()

# 2. The Artists render the output.
# Option A: Plot with Matplotlib
graphinate.renderers.matplotlib.plot(graph)

# Option B: Generate a Mermaid diagram
mermaid_string = graphinate.builders.MermaidBuilder(model).build()
print(mermaid_string)
```

## 5. Gotchas & Best Practices

- **The Command Center (`graphinate.cli`)**: For quick builds or serving, use the CLI:
    - `graphinate build --model <path/to/model.py>`
    - `graphinate serve --model <path/to/model.py>`
- **The Broadcaster (`graphinate.server`)**: The `serve` command requires optional dependencies. If it fails, the user
  needs to run:
  ```bash
  pip install "graphinate[server]"
  ```
- **Extractor Flexibility**: The `key`, `label`, `type_`, `source`, and `target` parameters can be simple strings (for
  dictionary keys) or powerful callable functions for complex data transformation.
- **Lazy Evaluation**: Data is not processed until a builder's `.build()` method is called. The definition phase is
  lightweight. This is a core feature.
- **"Magic" Injection**: The current dependency injection is a known issue (`GEP-010`). Be explicit. Ensure that the
  arguments in your node and edge functions match the properties of the items yielded by your source functions.
- **Declarative First**: Your primary role is to define the graph structure using the `GraphModel` and its decorators.
  Avoid writing imperative loops to build the graph manually. Trust the engine.