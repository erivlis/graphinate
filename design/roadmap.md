# Graphinate Development Roadmap

This document outlines the strategic execution plan for the Graphinate Enhancement Proposals (GEPs). The GEPs are
prioritized based on Impact, Difficulty, and Urgency.

## Phase 1: Stabilization (Critical & High Urgency)

*Focus: Fixing brittle code, security risks, and "bad magic". These tasks address technical debt that threatens
stability.*

| GEP         | Title                                  | Impact   | Difficulty | Rationale                                                                                                               |
|:------------|:---------------------------------------|:---------|:-----------|:------------------------------------------------------------------------------------------------------------------------|
| **GEP-013** | **Stable ID Serialization**            | **High** | Medium     | **Critical Security/Stability.** The current `repr()` + `eval()` mechanism is unsafe and unstable. Must be fixed first. |
| **GEP-010** | **Explicit Dependency Injection**      | **High** | Medium     | **High Usability.** The current string-matching injection is the #1 source of user confusion and runtime errors.        |
| **GEP-016** | **CLI Argument Parsing & Path Safety** | Low      | Easy       | **Quick Win.** Improves CLI usability and safety with minimal effort.                                                   |
| **GEP-017** | **Decoupled Server Architecture**      | Medium   | Easy       | **Enabler.** Decoupling the server unlocks proper integration testing for future phases.                                |

## Phase 2: Refactoring (Architectural Health)

*Focus: Refactoring complex subsystems to make future features easier to implement.*

| GEP         | Title                                  | Impact   | Difficulty | Rationale                                                                                                                            |
|:------------|:---------------------------------------|:---------|:-----------|:-------------------------------------------------------------------------------------------------------------------------------------|
| **GEP-024** | **The Graph Engine**                   | **High** | **Hard**   | **Core Architecture.** Extracting the execution logic is the foundation for Async, Realtime, and better testing. Supersedes GEP-015. |
| **GEP-014** | **Explicit GraphQL Schema Generation** | **High** | **Hard**   | **Major Refactor.** The current "Voodoo" class generation is fragile. Refactoring this is a prerequisite for Relay support.          |
| **GEP-020** | **Modular Frontend Architecture**      | Medium   | Medium     | **Maintainability.** The monolithic `index.html` is unmanageable. Refactoring enables better UI features.                            |
| **GEP-019** | **Offline Viewer Support**             | Medium   | Easy       | **Reliability.** Removing CDN dependencies ensures the viewer works in air-gapped environments.                                      |

## Phase 3: Expansion (New Features)

*Focus: Adding significant new capabilities that deliver value to users.*

| GEP         | Title                            | Impact   | Difficulty | Rationale                                                                                            |
|:------------|:---------------------------------|:---------|:-----------|:-----------------------------------------------------------------------------------------------------|
| **GEP-018** | **Relay Support**                | **High** | Medium     | **Enterprise Feature.** Makes the API compatible with modern frontend clients (React Relay, Apollo). |
| **GEP-023** | **Async Support**                | **High** | **Hard**   | **Performance.** Massive gains for I/O-bound crawling. Dependent on GEP-024.                         |
| **GEP-022** | **2D Visualization Mode**        | Medium   | Medium     | **Usability.** 2D is often better for analysis than 3D.                                              |
| **GEP-011** | **Standardized Element Factory** | Low      | Easy       | **Cleanup.** Minor API improvement.                                                                  |
| **GEP-012** | **Robust Model Composition**     | Low      | Easy       | **Cleanup.** Handling edge cases in model merging.                                                   |

## Summary Matrix

| Priority | GEP         | Title                              |
|:---------|:------------|:-----------------------------------|
| 1        | **GEP-013** | Stable ID Serialization            |
| 2        | **GEP-010** | Explicit Dependency Injection      |
| 3        | **GEP-017** | Decoupled Server Architecture      |
| 4        | **GEP-016** | CLI Argument Parsing & Path Safety |
| 5        | **GEP-024** | The Graph Engine                   |
| 6        | **GEP-014** | Explicit GraphQL Schema Generation |
| 7        | **GEP-020** | Modular Frontend Architecture      |
| 8        | **GEP-019** | Offline Viewer Support             |
| 9        | **GEP-018** | Relay Support                      |
| 10       | **GEP-023** | Async Support                      |

## Superseded / Withdrawn

* **GEP-015:** Refactored Graph Population Strategies (Superseded by GEP-024)
