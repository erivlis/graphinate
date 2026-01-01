# GEP-007: Theoretical Foundations

| Field       | Value                   |
|:------------|:------------------------|
| **GEP**     | 7                       |
| **Title**   | Theoretical Foundations |
| **Author**  | Eran Rivlis             |
| **Status**  | Active                  |
| **Type**    | Informational           |
| **Created** | 2026-01-01              |

## Abstract

This document explores the mathematical and theoretical underpinnings of Graphinate. By framing the library's operations in terms of **Category Theory** and **Type Theory**, we gain a rigorous vocabulary for discussing composition, transformation, and extraction. This is not a specification for code, but a specification for *thought*.

## 1. The Graph as a Category

In Graphinate, a `GraphModel` can be viewed as a **Category** (or at least a Quiver/Multigraph).

*   **Objects (Nodes):** The entities extracted from the source.
*   **Morphisms (Edges):** The relationships between entities.
*   **Composition:** The ability to traverse paths ($f: A \to B, g: B \to C \implies g \circ f: A \to C$).

## 2. Extraction as a Functor

The "Extraction" phase (GEP-029) is a mapping from the **Implicit Category** (the Source Data) to the **Explicit Category** (the GraphModel).

*   **Source Category ($\mathcal{S}$):** The raw data universe (e.g., the Web, a Database).
*   **Target Category ($\mathcal{G}$):** The Graphinate Model.
*   **The Extractor ($E: \mathcal{S} \to \mathcal{G}$):** A **Functor** that preserves structure.
    *   It maps Source Objects (URLs) to Target Objects (Nodes).
    *   It maps Source Links (Hyperlinks) to Target Morphisms (Edges).

## 3. Builders as Natural Transformations

A `Builder` (NetworkX, GraphQL, D3) transforms the abstract `GraphModel` into a concrete representation.

If we consider different representations as different Functors from the Model to the "World of Data Structures", then a Builder is the implementation of that Functor.

## 4. Composition as Pushouts

Graphinate supports model composition (`model_a + model_b`). In Category Theory, merging two graphs along shared nodes is a **Pushout**.

*   If Model A has Node $X$ and Model B has Node $X$, the sum $A+B$ glues them together at $X$.
*   This rigorous definition helps us handle edge cases in **GEP-012 (Robust Model Composition)**.

## 5. Taxonomy as Type Theory (GEP-030)

The Node Type Taxonomy is a **Type System**.

*   **Types:** `Entity`, `Event`, `Person`.
*   **Subtyping:** `Person <: Entity`.
*   **Dependent Types:** Edge definitions can be seen as dependent types: $Edge(u, v)$ is valid only if $u: TypeA$ and $v: TypeB$.

## 6. Aggregation as Quotient Graphs

Simplifying a graph (e.g., "Group all Files by Folder") is a **Graph Homomorphism** onto a **Quotient Graph**.

*   We map multiple nodes in the source graph to a single node in the quotient graph.
*   Edges between source nodes become edges between the quotient nodes.

## Why This Matters

Thinking in these terms prevents ad-hoc design.
*   When we design **Filtering**, we are defining a **Subobject**.
*   When we design **Views**, we are defining **Projections**.
*   When we design **Pipelines**, we are composing **Functors**.

Graphinate is not just a library; it is a **Structure-Preserving Map** from Data to Knowledge.
