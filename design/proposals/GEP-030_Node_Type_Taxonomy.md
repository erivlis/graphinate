# GEP-030: Node Type Taxonomy

| Field       | Value              |
|:------------|:-------------------|
| **GEP**     | 30                 |
| **Title**   | Node Type Taxonomy |
| **Author**  | Eran Rivlis        |
| **Status**  | Draft              |
| **Type**    | Standards Track    |
| **Created** | 2026-01-01         |
| **Updated** | 2026-01-01         |

> **⚠️ WORK IN PROGRESS**
> This proposal is in an early conceptual stage. The taxonomy and implementation details are subject to significant change.

## Abstract

This proposal introduces a hierarchical Type System for Graphinate nodes. By moving from simple string-based types to a structured taxonomy (e.g., `Person` is an `Entity`), we enable semantic styling, filtering, and layout algorithms that operate on abstract categories rather than specific labels.

## Motivation

Currently, `type="User"` and `type="Server"` are just strings to Graphinate. The engine doesn't know that a User is an "Actor" and a Server is an "Infrastructure".

**Benefits of a Taxonomy:**
1.  **Semantic Styling:** "Color all `Infrastructure` nodes grey."
2.  **Semantic Filtering:** "Hide all `Events`."
3.  **Layout:** "Group `Actors` together."

## Conceptual Taxonomy (The Core)

We propose a standard library `graphinate.taxonomy` containing generic base classes:

*   **`Entity`** (The "Thing")
    *   `Person`
    *   `Organization`
    *   `Place`
    *   `Artifact` (File, Document)
    *   `Concept` (Idea, Tag)
*   **`Event`** (The "Happening")
    *   `Transaction`
    *   `Interaction`
*   **`Structure`** (The "Container")
    *   `Group`
    *   `System`

## Domain-Specific Taxonomies (Extensions)

The power of this system lies in extensions. We can provide standard implementations for popular domains.

### 1. The C4 Model (Software Architecture)
Maps software architecture concepts to the core.
*   `C4.Person` -> `Entity.Person`
*   `C4.SoftwareSystem` -> `Structure.System`
*   `C4.Container` -> `Structure.Container`
*   `C4.Component` -> `Structure.Module`

### 2. Pygments (Code Analysis)
Maps syntax highlighting tokens to the core for AST visualization.
*   `Token.Keyword` -> `Entity.Concept`
*   `Token.Name.Function` -> `Entity.Artifact` (or `Behavior`)
*   `Token.Literal` -> `Entity.Artifact`

### 3. Schema.org (Knowledge Graphs)
Maps the web's vocabulary to the core.
*   `schema:Person` -> `Entity.Person`
*   `schema:CreativeWork` -> `Entity.Artifact`
*   `schema:Event` -> `Event`

## Implementation Ideas

*   Python Class Hierarchy (`class User(Person): ...`).
*   Mixins for custom taxonomies.
*   Integration with `GraphModel` decorators.

## Open Questions

*   How rigid should this be?
*   Should it support multiple inheritance (Poly-hierarchy)?
*   How does this map to GraphQL interfaces?
