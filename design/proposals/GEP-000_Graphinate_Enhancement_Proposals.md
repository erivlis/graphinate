---
title: "GEP-000: Graphinate Enhancement Proposals"
description: "Process and governance for authoring, reviewing, and implementing Graphinate Enhancement Proposals (GEPs), specialized from the PEP and EP standards."
icon: lucide/git-branch
status: active
---

# GEP-000: Graphinate Enhancement Proposals

| Field       | Value                            |
|:------------|:---------------------------------|
| **GEP**     | 0                                |
| **Title**   | Graphinate Enhancement Proposals |
| **Author**  | Eran Rivlis                      |
| **Delegate**| The Council                      |
| **Status**  | Active                           |
| **Type**    | Process                          |
| **Created** | 2025-12-25                       |
| **Updated** | 2026-10-21                       |

## Abstract

This document defines the formal process, structure, and lifecycle for creating, reviewing, validating, and implementing
Graphinate Enhancement Proposals (GEPs). GEPs are Graphinate's primary mechanism for proposing major features,
establishing architectural standards, documenting technical rationale, and preventing design regression.

GEP-000 rebases Graphinate's proposal system directly on the universal **Enhancement Proposals (EP)** standard
(modeled after [PEP 1](https://peps.python.org/pep-0001/)), specializing it by binding proposal review and rationale
directly to the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)).

## Motivation

As Graphinate evolves from a synchronous builder utility into a high-performance graph synthesis engine, proposal
ad-hocism risks architectural drift, unclear contracts, and regressions. 

**Issues with Unstandardized Proposals:**
1. **Omitted Alternatives & Rejections:** Without a mandatory `Rejected Ideas` section, previously discarded approaches
   are repeatedly proposed or partially implemented.
2. **Untracked Open Decisions:** Technical trade-offs remain implicit in PRs rather than resolved during proposal review.
3. **Inconsistent Lifecycles:** Proposals remain in `Draft` indefinitely even after code is merged or discarded.
4. **Leakage:** Internal proposal numbering can leak into public domain code and user-facing API documentation.

## Rationale

Rebasing GEPs on the EP standard while embedding the Council Framework directly aligns with the 7 Council Pillars:

- **Symmetry (Noether):** The GEP lifecycle mirrors the standard PEP state machine (`Draft` → `Review` → `Accepted` → `Implemented` → `Final`), ensuring uniform progress tracking.
- **Falsifiability (Popper):** Every proposal must specify clear acceptance criteria, testable constraints, and falsifiable design assertions before transitioning to `Accepted`.
- **Efficiency (Shannon):** Automated validation via `.agents/skills/enhancement-proposals/scripts/validate_ep.py` ensures proposal completeness without manual editorial toil.
- **Safety (The Golem):** Mandatory `Backwards Compatibility` and `Rejected Ideas` sections guard against breaking public APIs and re-introducing known hazards.
- **Clarity (Feynman):** Clear separation between proposal files (`design/proposals/`), user documentation (`docs/`), and application source (`src/`).
- **Consistency (Russell):** Unified YAML frontmatter and Markdown metadata tables across all proposals.
- **Harmony (The Steward):** Preserves an immutable, historical record of design consensus and architectural evolution.

## Specification

### 1. The GEP Standard & Relationship to EP

GEPs are a domain-specific specialization of the universal Enhancement Proposal (EP) skill:
* **Storage Location:** All GEP proposals reside in `design/proposals/` named `GEP-XXX_<Title_Slug>.md`.
* **Tooling & Validation:** Governed by the `.agents/skills/enhancement-proposals` skill and validated via `validate_ep.py`.
* **Council Binding:** The `Rationale` section must explicitly evaluate the design against the **7 Council Pillars** ([GEP-001](GEP-001_The_Graphinate_Mission.md)).

### 2. GEP Types

1. **Standards Track:** Core library features, builder APIs, engine modifications, or data contracts.
2. **Process:** Meta-proposals (such as GEP-000 or GEP-003) describing development procedures, roadmap priorities, or governance.
3. **Informational:** Architectural philosophies, theoretical foundations ([GEP-007](GEP-007_Theoretical_Foundations.md)), or best practices.

### 3. GEP Lifecycle & State Machine

```
           ┌──────────┐
           │  Draft   │
           └────┬─────┘
                │
                ▼
           ┌──────────┐
      ┌───>│  Review  │<──┐
      │    └────┬─────┘   │
      │         │         │
      │   ┌─────┼─────────┼─────────┐
      │   │     │         │         │
      │   ▼     ▼         ▼         ▼
┌─────┴────┐ ┌────────┐ ┌─────────┐ ┌────────────┐
│ Deferred │ │Accepted│ │Rejected │ │ Withdrawn  │
└──────────┘ └──┬─────┘ └─────────┘ └────────────┘
                │
                ▼
         ┌────────────┐
         │Implemented │
         └──────┬─────┘
                │
                ▼
          ┌──────────┐
          │  Active  │ (or Final / Superseded)
          └──────────┘
```

- **`Draft`:** Proposal under active authoring and informal exploration.
- **`Review`:** Submitted for formal evaluation by the Council.
- **`Accepted`:** Approved by Council consensus. Ready for implementation.
- **`Rejected`:** Formally declined. Rationales recorded in `Rejected Ideas`.
- **`Deferred`:** Postponed for a future roadmap phase.
- **`Withdrawn`:** Retracted by author.
- **`Implemented`:** Code merged into the codebase with complete test coverage.
- **`Active` / `Final`:** Complete, active standard or process in production.
- **`Superseded`:** Replaced by a newer GEP (`Superseded-By` populated).

### 4. Mandatory Proposal Structure

Every GEP must contain:
1. **YAML Frontmatter:** `title`, `description`, `icon`, `status`.
2. **Metadata Header Table:** `GEP`, `Title`, `Author`, `Delegate`, `Status`, `Type`, `Created`, `Updated`.
3. **Mandatory Sections:**
   - `## Abstract`
   - `## Motivation`
   - `## Rationale` (evaluating Council Pillars: Noether, Popper, Shannon, Golem, Feynman, Russell, Steward)
   - `## Specification`
   - `## Backwards Compatibility`
   - `## How to Teach This / Documentation Plan`
   - `## Reference Implementation`
   - `## Rejected Ideas`
   - `## Open Questions`
   - `## Change Log`

### 5. Non-Leakage & Abstraction Rules

1. **No GEP Leaks in Application Source:** Source code in `src/graphinate/` must describe behavior using standard graph theory, computer science, and Python terms. EP/GEP numbers must not be used as class names, function names, or primary docstring rationale.
2. **No GEP Leaks in User-Facing Guides:** Public tutorials and guides in `docs/` describe features purely from the user's perspective.
3. **Encapsulation:** GEP files live exclusively in `design/proposals/`.

## Backwards Compatibility

All existing GEPs retain their canonical numbering. Existing GEPs will be progressively updated to conform to frontmatter, the Council review matrix, and the mandatory sections during Phase 2 review cycles.

## How to Teach This / Documentation Plan

- The `.agents/skills/enhancement-proposals` skill has been installed in the repository under `.agents/skills/enhancement-proposals`.
- GEP authors can scaffold new proposals using `.agents/skills/enhancement-proposals/templates/gep-template.md`.
- Automated validation is executed using `uv run python .agents/skills/enhancement-proposals/scripts/validate_ep.py <path>`.

## Reference Implementation

- Template: [`.agents/skills/enhancement-proposals/templates/gep-template.md`](file:///C:/dev/erivlis/graphinate/.agents/skills/enhancement-proposals/templates/gep-template.md)
- Validator: [`.agents/skills/enhancement-proposals/scripts/validate_ep.py`](file:///C:/dev/erivlis/graphinate/.agents/skills/enhancement-proposals/scripts/validate_ep.py)
- Specification Guide: [`.agents/skills/enhancement-proposals/references/ep-lifecycle-and-validation.md`](file:///C:/dev/erivlis/graphinate/.agents/skills/enhancement-proposals/references/ep-lifecycle-and-validation.md)

## Rejected Ideas

- **Informal Markdown Notes:** Rejected because unstandardized notes lead to missing specifications, unhandled backwards compatibility bugs, and lost historical trade-offs.
- **Strict Web Nav Registration Requirement:** While universal EPs register into `zensical.toml`, Graphinate uses `properdocs.yml` (MkDocs Material) where `design/proposals` are internal engineering documents rather than public user docs. The validator was made resilient to avoid requiring internal proposals in user navigation.

## Open Questions

- [x] Should GEP proposals be compiled into MkDocs Material (`properdocs.yml`)? *Decision: No, GEPs remain internal engineering specs under `design/proposals/` to maintain the non-leakage invariant.*

## Change Log

* **2025-12-25:** Initial draft.
* **2025-12-28:** Updated workflow statuses.
* **2026-10-21:** Rebased GEP standard over universal EP skill (`.agents/skills/enhancement-proposals`), established formal Council Framework review requirements, and added automated validation.
