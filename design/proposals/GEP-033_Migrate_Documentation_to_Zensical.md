---
title: "GEP-033: Migrate Documentation to Zensical"
description: "Migrate the static documentation generation and deployment pipeline from MkDocs/properdocs to Zensical."
icon: lucide/book-open
status: draft
---

# GEP-033: Migrate Documentation to Zensical

| Field        | Value                             |
|:-------------|:----------------------------------|
| **GEP**      | 33                                |
| **Title**    | Migrate Documentation to Zensical |
| **Author**   | Eran Rivlis                       |
| **Delegate** | The Council                       |
| **Status**   | Draft                             |
| **Type**     | Process                           |
| **Created**  | 2026-10-24                        |
| **Updated**  | 2026-10-24                        |

## Abstract

This proposal specifies the migration of Graphinate's documentation site generation, theme configuration, and deployment
pipeline from MkDocs / properdocs (`properdocs.yml`) to **Zensical** (`zensical.toml`). This migration unifies the
project's configuration landscape around modern TOML standards, eliminates a heavyweight transitive plugin dependency
tree, accelerates local preview and CI/CD deployment pipelines, and standardizes site navigation across the ecosystem.

## Motivation

Graphinate currently maintains its public documentation site via `properdocs.yml`, an MkDocs Material distribution.
While functional, this infrastructure presents several operational drawbacks:

1. **Heavyweight Transitive Dependency Tree:** The current `docs` dependency group in `pyproject.toml` requires 9+
   separate Python packages (`mkdocs-materialx`, `mkdocstrings-python`, `mkdocs-gen-files`, `mkdocs-glightbox`,
   `mkdocs-literate-nav`, `mkdocs-section-index`, `mkdocs-git-committers-plugin-2`, `mike`, and `properdocs`). This
   inflates install size, increases resolution times, and exposes the build pipeline to cross-plugin incompatibility
   risks.
2. **Configuration Fragmentation (YAML vs. TOML):** The Python ecosystem and Graphinate have standardized on TOML for
   project metadata, tool configuration, linters, and dependencies (`pyproject.toml`). Retaining a bespoke YAML
   configuration file (`properdocs.yml`) fragments repository configuration semantics.
3. **Ecosystem & Skill Alignment:** Repository tooling and agent workflows (such as `.agents/skills/enhancement-proposals`)
   already adopt Zensical conventions as the canonical project documentation architecture.
4. **Build & Deployment Latency:** MkDocs with dynamic generation scripts (`docs/gen_ref_pages.py`, `docs/gen_examples_nav.py`)
   and multiple plugin hooks incurs noticeable build overhead during local development iterations and CI documentation
   publishing.

Migrating to Zensical simplifies the toolchain into a single, cohesive, TOML-configured static documentation engine.

## Rationale

Evaluating the migration against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):

- **Symmetry (Noether):** The structural site hierarchy (Start, Guide, Advanced, Reference, Development) maps
  symmetrically from the existing MkDocs navigation into `zensical.toml` without breaking external page URLs.
- **Falsifiability (Popper):** Migration completeness can be falsified through automated link checks, asset verification
  (Mermaid diagrams, stylesheets, images), and build validation in CI (`uv run zensical build`).
- **Efficiency (Shannon):** Replaces a large tree of MkDocs plugins with Zensical's unified pipeline, minimizing cold-start
  times in GitHub Actions (`publish-docs.yaml`) and speeding up local live-reload cycles.
- **Safety (The Golem):** Consolidating dependencies reduces the supply chain attack surface and mitigates breaking
  upstream plugin API changes across minor MkDocs ecosystem releases.
- **Clarity (Feynman):** A single `zensical.toml` file contains the complete site configuration, palette, and navigation
  in clean, readable TOML rather than nested YAML with custom Python hook scripts.
- **Consistency (Russell):** Aligns documentation configuration format (`.toml`) with `pyproject.toml` and standard
  repository workflows.
- **Harmony (The Steward):** Preserves Graphinate's established brand identity, dark/light palette, custom typography,
  and documentation integrity while modernizing underlying infrastructure.

## Specification

### 1. Configuration: `zensical.toml`

Replace `properdocs.yml` with `zensical.toml` in the repository root:

```toml
[project]
name = "Graphinate"
description = "Graphinate. Data to Graphs. A Python library for creating and manipulating graphs from various data sources."
site_url = "https://erivlis.github.io/graphinate"
author = "Eran Rivlis"
copyright = "Copyright © 2023-2026 Eran Rivlis"

[theme]
name = "zensical"
logo = "assets/images/logo-128.png"
favicon = "assets/images/logo-128.png"
extra_css = ["assets/stylesheets/extra.css"]

[theme.palette]
default = "slate"
primary = "custom"
accent = "deep purple"
toggle_light_scheme = "default"
toggle_dark_scheme = "slate"

[features]
content_action_view = true
content_code_copy = true
navigation_tabs = true
navigation_top = true
search = true
toc_depth = 3

[markdown.extensions]
admonitions = true
code_highlight = true
mermaid = true
tables = true
math = false

[navigation]
start = [
    { title = "Home", path = "index.md" },
    { title = "Introduction", path = "introduction.md" },
    { title = "Quick Start", path = "start.md" },
    { title = "Tutorial", path = "tutorial.md" }
]
guide = [
    { title = "Usage", path = "usage/index.md" },
    { title = "Examples", path = "examples/index.md" }
]
advanced = [
    { title = "Modeling", path = "advanced/modeling.md" },
    { title = "The Graph Engine", path = "advanced/engine.md" },
    { title = "GraphQL", path = "advanced/graphql.md" },
    { title = "Optimization", path = "advanced/optimization.md" },
    { title = "Secure IDs", path = "advanced/secure_ids.md" }
]
development = [
    { title = "Development", path = "development.md" },
    { title = "Acknowledgements", path = "acknowledgements.md" }
]
```

### 2. Dependency Groups (`pyproject.toml`)

Update the `[dependency-groups.docs]` table in `pyproject.toml` to replace the MkDocs ecosystem with Zensical:

```toml
[dependency-groups]
docs = [
    "zensical"
]
```

### 3. CI/CD Workflow (`.github/workflows/publish-docs.yaml`)

Update the GitHub Actions deployment workflow:

```yaml
name: Publish Docs
on:
  push:
    branches:
      - main
permissions:
  contents: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7
      - name: Set up UV and Python
        uses: astral-sh/setup-uv@v10.3.0
        with:
          python-version: "3.15"
      - name: Install dependencies and deploy docs
        run: |
          uv sync --only-group docs
          uv run zensical deploy --force
```

### 4. Content Structure & Non-Leakage Boundary

- All documentation markdown content remains residing in `docs/`.
- Per [GEP-000](GEP-000_Graphinate_Enhancement_Proposals.md), internal design proposals in `design/proposals/` remain
  internal architecture documentation and are not exposed in the default public user documentation navigation.
- Custom CSS in `docs/assets/stylesheets/extra.css` is retained and linked in `zensical.toml`.

## Backwards Compatibility

- **Public URLs:** All existing documentation routes (`/`, `/introduction/`, `/start/`, `/tutorial/`,
  `/advanced/engine/`, `/advanced/optimization/`, etc.) will remain identical, preserving existing external links and
  search engine indices.
- **Markdown Sources:** All existing documentation pages in `docs/` use standard GitHub Flavored Markdown (GFM),
  admonitions (`!!! note`), and Mermaid diagrams (` ```mermaid `), which are natively supported by Zensical.
- **Core Library:** Zero impact on `graphinate` runtime, public APIs, builders, engine, or CLI.

## How to Teach This / Documentation Plan

- Update `CONTRIBUTING.md` / `docs/development.md` to document local preview instructions:
  ```bash
  uv sync --only-group docs
  uv run zensical serve
  ```
- Update `.agents/skills/enhancement-proposals/scripts/validate_ep.py` to ensure `check_zensical_nav` works seamlessly
  with the new configuration.

## Reference Implementation

- Target configuration file: [`zensical.toml`](zensical.toml)
- Dependency specifications: [`pyproject.toml`](pyproject.toml)
- Deployment workflow: [`.github/workflows/publish-docs.yaml`](.github/workflows/publish-docs.yaml)
- Existing documentation source: [`docs/index.md`](docs/index.md)

## Rejected Ideas

- **Retaining MkDocs with Minimal Plugins:** Rejected because the core MkDocs configuration paradigm remains rooted in
  YAML and legacy Python plugin bindings, missing out on modern unified TOML tooling.
- **Migrating to Sphinx or Sphinx-Book:** Rejected due to heavyweight reStructuredText legacy syntax, slow build times,
  and unnecessary complexity for Graphinate's clean Markdown documentation.
- **Publishing Internal GEPs Directly in User Navigation:** Rejected per [GEP-000](GEP-000_Graphinate_Enhancement_Proposals.md).
  Internal engineering proposals serve architectural evolution and design consensus; user documentation must remain
  focused on library usage, tutorials, and public APIs.

## Open Questions

- [ ] Does Zensical support automated Python API reference generation equivalent to `mkdocstrings` out-of-the-box, or
  is a companion Zensical plugin required?
- [ ] Should multi-version documentation support (previously handled by `mike`) be handled by Zensical natively or
  managed via GitHub Actions branching?

## Change Log

* **2026-10-24:** Initial Draft by Eran Rivlis.
