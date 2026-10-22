---
title: "GEP-003: Graphinate Development Roadmap"
description: "Living development roadmap and multi-phase execution strategy for Graphinate Enhancement Proposals."
icon: lucide/map
status: active
---

# GEP-003: Graphinate Development Roadmap

| Field        | Value               |
|:-------------|:--------------------|
| **GEP**      | 3                   |
| **Title**    | Development Roadmap |
| **Author**   | Eran Rivlis         |
| **Delegate** | The Council         |
| **Status**   | Active              |
| **Type**     | Process             |
| **Created**  | 2025-12-30          |
| **Updated**  | 2026-10-22          |

## Abstract

This document outlines the strategic execution plan for the Graphinate Enhancement Proposals (GEPs). It serves as a
living document to track the prioritization and status of major initiatives.

## Phase 1: Stabilization (Completed)

*Focus: Fixing brittle code, security risks, and "bad magic". All Phase 1 stabilization proposals (**GEP-010**,
**GEP-016**, **GEP-017**, **GEP-019**, **GEP-025**, **GEP-032**) have been implemented and archived.*

## Phase 2: Core Spine & Architectural Health

*Focus: Strengthening the core execution engine, schema generation, and modularity.*

| GEP         | Title                                      | Impact   | Difficulty | Rationale                                                                                                                  |
|:------------|:-------------------------------------------|:---------|:-----------|:---------------------------------------------------------------------------------------------------------------------------|
| **GEP-014** | **Explicit GraphQL Schema Generation**     | **High** | **Hard**   | **Major Refactor.** Refactoring dynamic class generation to `strawberry.tools.create_type` and context-injected resolvers. |
| **GEP-023** | **Async Support**                          | **High** | **Hard**   | **Performance.** Massive gains for I/O-bound crawling (`async def` generators). Dependent on GEP-024.                      |
| **GEP-031** | **High-Performance Vectorized Operations** | Medium   | Medium     | **Performance.** Progressive enhancement via optional NumPy/Numba (partially active in `color.py`).                        |

## Phase 3: Focused Expansion

*Focus: Practical extensions that build directly on the core engine and schema.*

| GEP         | Title                             | Impact   | Difficulty | Rationale                                                                                              |
|:------------|:----------------------------------|:---------|:-----------|:-------------------------------------------------------------------------------------------------------|
| **GEP-018** | **Relay Support**                 | **High** | Medium     | **Enterprise Feature.** Makes the API compatible with modern frontend clients (React Relay, Apollo).   |
| **GEP-020** | **Modular Frontend Architecture** | Medium   | Medium     | **Maintainability.** Splitting the monolithic `viewer/index.html` into maintainable ES modules.        |
| **GEP-029** | **Extraction Strategies**         | Medium   | Medium     | **Ergonomics.** Lightweight iterator/generator helpers (`scan`, `walk`, `listen`) or cookbook recipes. |

## Phase 4: Exploratory & Spin-Off Track (Ideation / Brainstorming)

*Focus: Ideas originating from exploratory brainstorming sessions. Rather than bloating the core `graphinate` package,
these proposals should be treated as candidates for standalone companion packages, external integrations, or example
recipes.*

| GEP         | Title                                          | Recommended Vehicle                  | Rationale                                                                                                                     |
|:------------|:-----------------------------------------------|:-------------------------------------|:------------------------------------------------------------------------------------------------------------------------------|
| **GEP-026** | **Pluggable Visualization & Notebook Support** | Companion Package / Cookbook Recipes | Keeps core `graphinate` free of heavy frontend widget toolchains while enabling Jupyter/Cosmograph recipes.                   |
| **GEP-027** | **Advanced Three.js Visualizations**           | Standalone Frontend / Demo Showcase  | Custom WebGL shaders, procedural cities, and time tunnels belong in a dedicated visualization showcase, not a Python ETL lib. |
| **GEP-028** | **MCP Server Integration**                     | Companion Package (`graphinate-mcp`) | Ideal as a lightweight wrapper or example recipe exposing `GraphModel` and `GraphQLBuilder` to LLM agents via `fastmcp`.      |
| **GEP-030** | **Node Type Taxonomy**                         | Cookbook Recipes / Domain Extensions | Universal ontologies (C4, Schema.org, Pygments) are best demonstrated as user-space models/recipes rather than core classes.  |

---

## Strategic Assessment of the GEP Trajectory

### 1. Engineering Assessment: The Three Buckets

The trajectory from **Graphinate 0.x** (a synchronous, decorator-based NetworkX/GraphQL builder) toward **Graphinate
2.0** (an observable, async-capable, type-safe Graph Synthesis Engine) is architecturally cohesive and
well-differentiated in the Python ecosystem—provided that **implementation consolidation takes precedence over scope
expansion**.

Across the GEP archive, proposals fall naturally into three distinct tiers:

1. **The Core Structural Spine (`GEP-010` → `GEP-032` → `GEP-012` → `GEP-024` → `GEP-023`)**:
    - This is the true heart of Graphinate: moving from implicit `_id` naming magic to explicit `ParentId` dependency
      injection (**GEP-010**), compiling immutable validated models (**GEP-032**), decoupling traversal (`GraphEngine`,
      **GEP-024**) from storage (`NetworkxBuilder`), and unlocking `async def` generators (**GEP-023**).
    - Every link in this chain directly enables the next and strengthens the library's core value proposition.
2. **Boundary & Hygiene Refactorings (`GEP-002`, `GEP-014`, `GEP-016`, `GEP-017`, `GEP-019`, `GEP-020`, `GEP-031`)**:
    - Practical engineering debt paydown: exposing `create_app()` (**GEP-017**), replacing fragile dynamic class
      construction in `GraphQLBuilder` with `strawberry.tools.create_type` and context injection (**GEP-014**), and
      keeping heavy dependencies optional (**GEP-002**).
3. **Exploratory Ideation / Ambition Creep (`GEP-026`, `GEP-027`, `GEP-028`, `GEP-029`, `GEP-030`)**:
    - These proposals originated in exploratory brainstorming sessions. While intellectually rich, features like custom
      Three.js shaders/procedural cities (**GEP-027**), universal class ontologies mapping Schema.org/C4/Pygments
      (**GEP-030**), and multi-engine WebGL abstractions (**GEP-026**) risk pulling a focused ~1,200-line Python library
      into maintaining a sprawling JavaScript/WebGL framework or ontology library ("Second-System Syndrome").
    - **Strategic Decision:** Treat Tier 3 proposals as **Exploratory / Spin-Off Candidates** (separate high-level
      projects, plugin packages, or cookbook examples) so the core library stays lean and faithful to **GEP-001**.

### 2. The Council's Opinion (By Pillar)

Evaluating the codebase and GEP trajectory through the **7 Pillars of the Council Framework** (**GEP-001**):

| Council Member                 | Verdict | Critique & Trajectory Guidance                                                                                                                                                                                                                                                                                                            |
|:-------------------------------|:-------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1. Symmetry (Noether)**      | **A-**  | `@model.node` supports `ParentId`, hierarchy, multiplicity, and deferred compilation (**GEP-010**, **GEP-032**). Future work in **GEP-024** should consider bringing symmetric dependency/scoping ergonomics to `@model.edge`, and ensuring edges can naturally target hierarchical (`unique=False`) nodes whose keys are lineage tuples. |
| **2. Falsifiability (Popper)** |  **A**  | High branch coverage (~98%) and property-style tests provide a strong safety net. Every Standards Track GEP must be paired with falsifying regression tests before its status transitions to `Active`.                                                                                                                                    |
| **3. Efficiency (Shannon)**    | **A-**  | `color.py` (**GEP-031**), `VariableNameManager` (`tools.py`), and $O(\text{deg}(v))$ GraphQL neighbor resolution are fast and lean. The primary remaining efficiency win is **GEP-002**: moving heavy packages (`matplotlib`, `strawberry-graphql`) out of mandatory core install dependencies into optional extras.                      |
| **4. Safety (The Golem)**      | **A-**  | With **GEP-025** (HMAC-SHA256 signed IDs), **GEP-032** (immutable `model.compile()` clones), and isolated `GraphNodeType` schema enums, thread-safety and concurrency hazards have been substantially hardened—critical for Python 3.13t–3.15t free-threaded execution.                                                                   |
| **5. Clarity (Feynman)**       |  **A**  | The `@model.node` / `@model.edge` declarative DSL remains simple and expressive. Completing **GEP-014** (explicit GraphQL schema generation with context injection) will remove the last major pocket of closure metaprogramming in `builders/graphql.py`.                                                                                |
| **6. Consistency (Russell)**   | **A-**  | Case-insensitive parent resolution and explicit `_lineage` tuple propagation across recursion depths have unified behavior between `modeling.py` and `builders/networkx.py`.                                                                                                                                                              |
| **7. Harmony (The Steward)**   | **A-**  | **The Dennis Point:** Resist building custom 3D shaders (**GEP-027**) or rigid taxonomies (**GEP-030**) inside core before the execution spine (`compile()` → `GraphEngine` → `abuild()`) is complete. Keep Graphinate focused on its mission: *"A declarative, Pythonic ETL engine for synthesizing graphs from hierarchical data."*     |

---

## Summary Priority Matrix (Core Library)

| Priority | GEP         | Title                                     | Phase   |
|:---------|:------------|:------------------------------------------|:--------|
| 1        | **GEP-014** | Explicit GraphQL Schema Generation        | Phase 2 |
| 2        | **GEP-023** | Async Support                             | Phase 2 |
| 3        | **GEP-031** | High-Performance Vectorized Operations    | Phase 2 |
| 4        | **GEP-018** | Relay Support                             | Phase 3 |
| 5        | **GEP-020** | Modular Frontend Architecture             | Phase 3 |
| 6        | **GEP-029** | Extraction Strategies (Helpers / Recipes) | Phase 3 |

## Archive (Completed / Withdrawn / Superseded)

| GEP         | Title                                  | Status            | Reason                                                                  |
|:------------|:---------------------------------------|:------------------|:------------------------------------------------------------------------|
| **GEP-000** | Graphinate Enhancement Proposals       | **Active**        | Process definition.                                                     |
| **GEP-001** | The Graphinate Mission                 | **Active**        | Mission statement.                                                      |
| **GEP-002** | Modularization Strategy                | **Active**        | Architectural principle.                                                |
| **GEP-007** | Theoretical Foundations                | **Active**        | Informational / Theory.                                                 |
| **GEP-010** | Explicit Dependency Injection          | **Active**        | Implemented explicit dependency injection using `ParentId`.             |
| **GEP-011** | Standardized Element Factory           | **Active**        | Split polymorphic `element` into `tuple_element` and `named_element`.   |
| **GEP-012** | Robust Model Composition               | **Active**        | Implemented `GraphModel.merge()` and `CompositionStrategy`.             |
| **GEP-013** | Stable ID Serialization                | **Withdrawn**     | `repr()` deemed sufficient and more robust for Python types.            |
| **GEP-016** | CLI Argument Parsing & Path Safety     | **Active**        | Implemented Typer CLI with safe dynamic argument parsing & paths.       |
| **GEP-017** | Decoupled Server Architecture          | **Active**        | Exposed `create_app()` ASGI factory in `graphinate.renderers.graphql`.  |
| **GEP-019** | Offline Viewer Support                 | **Active**        | In-package vendoring under `static/vendor/` for 100% offline 3D viewer. |
| **GEP-024** | The Graph Engine                       | **Active**        | Decoupled traversal into `GraphEngine`, `GraphObserver`, and events.    |
| **GEP-025** | Signed ID Serialization                | **Active**        | Implemented as an optional, opt-in HMAC-SHA256 signature layer.         |
| **GEP-032** | GraphModel Compilation & Validation    | **Active**        | Implemented `GraphModel.compile()` and deferred validation.             |
| **GEP-015** | Refactored Graph Population Strategies | **Superseded**    | Replaced by **GEP-024** (The Graph Engine).                             |
| **GEP-022** | 2D Visualization Mode                  | **Superseded**    | Replaced by **GEP-026** (Pluggable Visualization).                      |
| **GEP-027** | Advanced Three.js Visualizations       | **Informational** | Exploratory design concepts (Spin-Off / Showcase Track).                |

## Change Log

* **2025-12-30:** Initial roadmap draft.
* **2026-10-17:** Completed Phase 1 (GEP-010, GEP-016, GEP-017, GEP-025, GEP-032). Added Council assessment and 4-phase
  trajectory.
* **2026-10-22:** Rebased all 27 GEPs on EP standard and GEP-000. Completed and activated GEP-019 (Offline Viewer
  Support), GEP-011 (Standardized Element Factory), and GEP-012 (Robust Model Composition).
* **2026-10-23:** Completed and activated GEP-024 (The Graph Engine).




