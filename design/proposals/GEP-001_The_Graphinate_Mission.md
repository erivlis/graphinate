# GEP-001: The Graphinate Mission

| Field       | Value                  |
|:------------|:-----------------------|
| **GEP**     | 1                      |
| **Title**   | The Graphinate Mission |
| **Author**  | Eran Rivlis            |
| **Status**  | Active                 |
| **Type**    | Informational          |
| **Created** | 2025-12-25             |

## Abstract

This document defines the core purpose, philosophy, and architectural pillars of the Graphinate library. It serves as
the "North Star" for all future development and GEPs.

## Mission Statement

**"To provide a declarative, Pythonic ETL engine for synthesizing graphs from hierarchical data."**

Graphinate exists to bridge the gap between structured data sources (APIs, Databases, Files) and Graph
Analysis/Visualization tools. It is not just a graph library; it is a **Graph Synthesis Engine**.

## Core Philosophy

### 1. Declarative over Imperative

Users should describe *what* the graph looks like (Nodes, Edges, Hierarchy), not *how* to build it loop-by-loop. The
`GraphModel` DSL is the primary interface.

### 2. Lazy over Eager

Graph generation should be lazy. By leveraging Python generators (`yield`), Graphinate can define massive graphs without
loading them entirely into memory until the build phase requires it.

### 3. The Intermediate Representation (IR)

We decouple the **Model** (Definition) from the **Renderer** (Presentation). `NetworkX` serves as the immutable IR. This
allows a single model to be rendered as a GraphQL API, a D3 visualization, or a Mermaid diagram without changing the
definition.

### 4. Magic with Consent

We automate the tedious parts of graph building (ID generation, context propagation, schema derivation). However, this "
Magic" must always have an escape hatch. Explicit configuration should always override implicit convention.

## Architectural Pillars (The Council)

All contributions must adhere to the **Council Framework**:

1. **Symmetry (Noether):** Balanced APIs.
2. **Falsifiability (Popper):** Testable designs.
3. **Efficiency (Shannon):** Minimal representation.
4. **Safety (The Golem):** Robustness and immutability.
5. **Clarity (Feynman):** Understandable abstractions.
6. **Consistency (Russell):** Logical coherence.
7. **Harmony (The Steward):** Pragmatic integration.

## The "Dennis Point"

We value critical dissent. If an abstraction feels wrong, "magical", or bloated, we stop and debate. We build for the
Architect who values robustness over speed.
