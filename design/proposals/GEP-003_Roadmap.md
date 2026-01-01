# GEP-003: Graphinate Development Roadmap

| Field       | Value                   |
|:------------|:------------------------|
| **GEP**     | 3                       |
| **Title**   | Development Roadmap     |
| **Author**  | Eran Rivlis             |
| **Status**  | Active                  |
| **Type**    | Process                 |
| **Created** | 2025-12-30              |
| **Updated** | 2026-01-01              |

## Abstract

This document outlines the strategic execution plan for the Graphinate Enhancement Proposals (GEPs). It serves as a living document to track the prioritization and status of major initiatives.

## Phase 1: Stabilization (Critical & High Urgency)

*Focus: Fixing brittle code, security risks, and "bad magic". These tasks address technical debt that threatens
stability.*

| GEP         | Title                                  | Impact   | Difficulty | Rationale                                                                                                               |
|:------------|:---------------------------------------|:---------|:-----------|:------------------------------------------------------------------------------------------------------------------------|
| **GEP-010** | **Explicit Dependency Injection**      | **High** | Medium     | **High Usability.** The current string-matching injection is the #1 source of user confusion and runtime errors.        |
| **GEP-016** | **CLI Argument Parsing & Path Safety** | Low      | Easy       | **Quick Win.** Improves CLI usability and safety with minimal effort.                                                   |
| **GEP-017** | **Decoupled Server Architecture**      | Medium   | Easy       | **Enabler.** Decoupling the server unlocks proper integration testing for future phases.                                |

## Phase 2: Refactoring (Architectural Health)

*Focus: Refactoring complex subsystems to make future features easier to implement.*

| GEP         | Title                                  | Impact   | Difficulty | Rationale                                                                                                                            |
|:------------|:---------------------------------------|:---------|:-----------|:-------------------------------------------------------------------------------------------------------------------------------------|
| **GEP-024** | **The Graph Engine**                   | **High** | **Hard**   | **Core Architecture.** Extracting the execution logic is the foundation for Async, Realtime, and better testing. Supersedes GEP-015. |
| **GEP-029** | **Extraction Strategies**              | **High** | Medium     | **Core Architecture.** Formalizing the "E" in ETL. Prerequisite for robust crawling and streaming.                                   |
| **GEP-030** | **Node Type Taxonomy**                 | Medium   | Medium     | **Semantic Power.** Defines the Type System. Prerequisite for Schema Generation (GEP-014) and Styling (GEP-026).                     |
| **GEP-014** | **Explicit GraphQL Schema Generation** | **High** | **Hard**   | **Major Refactor.** The current "Voodoo" class generation is fragile. Refactoring this is a prerequisite for Relay support.          |
| **GEP-020** | **Modular Frontend Architecture**      | Medium   | Medium     | **Maintainability.** The monolithic `index.html` is unmanageable. Refactoring enables better UI features.                            |
| **GEP-019** | **Offline Viewer Support**             | Medium   | Easy       | **Reliability.** Removing CDN dependencies ensures the viewer works in air-gapped environments.                                      |

## Phase 3: Expansion (New Features)

*Focus: Adding significant new capabilities that deliver value to users.*

| GEP         | Title                                          | Impact   | Difficulty | Rationale                                                                                            |
|:------------|:-----------------------------------------------|:---------|:-----------|:-----------------------------------------------------------------------------------------------------|
| **GEP-026** | **Pluggable Visualization & Notebook Support** | **High** | **Hard**   | **Major Feature.** Enables Jupyter integration and high-performance rendering (Cosmograph).          |
| **GEP-028** | **MCP Server Integration**                     | **High** | Medium     | **AI Integration.** Allows LLMs to use Graphinate as a structural backend.                           |
| **GEP-018** | **Relay Support**                              | **High** | Medium     | **Enterprise Feature.** Makes the API compatible with modern frontend clients (React Relay, Apollo). |
| **GEP-023** | **Async Support**                              | **High** | **Hard**   | **Performance.** Massive gains for I/O-bound crawling. Dependent on GEP-024.                         |
| **GEP-011** | **Standardized Element Factory**               | Low      | Easy       | **Cleanup.** Minor API improvement.                                                                  |
| **GEP-012** | **Robust Model Composition**                   | Low      | Easy       | **Cleanup.** Handling edge cases in model merging.                                                   |

## Summary Matrix

| Priority | GEP         | Title                                      |
|:---------|:------------|:-------------------------------------------|
| 1        | **GEP-010** | Explicit Dependency Injection              |
| 2        | **GEP-017** | Decoupled Server Architecture              |
| 3        | **GEP-016** | CLI Argument Parsing & Path Safety         |
| 4        | **GEP-024** | The Graph Engine                           |
| 5        | **GEP-029** | Extraction Strategies                      |
| 6        | **GEP-030** | Node Type Taxonomy                         |
| 7        | **GEP-014** | Explicit GraphQL Schema Generation         |
| 8        | **GEP-026** | Pluggable Visualization & Notebook Support |
| 9        | **GEP-028** | MCP Server Integration                     |
| 10       | **GEP-020** | Modular Frontend Architecture              |

## Archive (Completed / Withdrawn / Superseded)

| GEP         | Title                                  | Status            | Reason                                                               |
|:------------|:---------------------------------------|:------------------|:---------------------------------------------------------------------|
| **GEP-000** | Graphinate Enhancement Proposals       | **Active**        | Process definition.                                                  |
| **GEP-001** | The Graphinate Mission                 | **Active**        | Mission statement.                                                   |
| **GEP-002** | Modularization Strategy                | **Active**        | Architectural principle.                                             |
| **GEP-007** | Theoretical Foundations                | **Active**        | Informational / Theory.                                              |
| **GEP-013** | Stable ID Serialization                | **Withdrawn**     | `repr()` deemed sufficient and more robust for Python types.         |
| **GEP-025** | Signed ID Serialization                | **Withdrawn**     | Overengineering. Security risk is low for this domain.               |
| **GEP-015** | Refactored Graph Population Strategies | **Superseded**    | Replaced by **GEP-024** (The Graph Engine).                          |
| **GEP-022** | 2D Visualization Mode                  | **Superseded**    | Replaced by **GEP-026** (Pluggable Visualization).                   |
| **GEP-027** | Advanced Three.js Visualizations       | **Informational** | Design concepts for **GEP-026**.                                     |
