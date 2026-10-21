---
title: "GEP-019: Offline Viewer Support"
description: "Vendor core 3D graph viewer JavaScript dependencies locally to guarantee reliable, air-gapped, and offline visualization."
icon: lucide/eye-off
status: active
---

# GEP-019: Offline Viewer Support

| Field       | Value                                      |
|:------------|:-------------------------------------------|
| **GEP**     | 19                                         |
| **Title**   | Offline Viewer Support                     |
| **Author**  | Eran Rivlis                                |
| **Delegate**| The Council                                |
| **Status**  | Active                                     |
| **Type**    | Standards Track                            |
| **Created** | 2025-12-25                                 |
| **Updated** | 2026-10-22                                 |

## Abstract

The Graphinate 3D Force-Directed Graph Viewer currently fetches frontend JavaScript libraries (`3d-force-graph`,
`tweakpane`, `murmurhash-js`, `three`, and `d3`) from public CDNs (`cdn.jsdelivr.net` and `esm.sh`). This prevents the
viewer from rendering in air-gapped environments, introduces external availability failure modes, and poses security
concerns.

This proposal establishes a vendored distribution architecture for the core 3D viewer assets under
`src/graphinate/server/web/static/vendor/`, eliminating external CDN network calls during graph exploration while
preserving lightweight distribution.

## Motivation

Graphinate is frequently deployed in secure data analysis environments, enterprise intranets, and disconnected laptops:
1. **Offline and Air-Gapped Environments:** When running without internet access, navigating to `http://localhost:8072/viewer`
   fails because external CDN scripts cannot be retrieved.
2. **Third-Party CDN Fragility:** Outages, domain blocking, or integrity mismatches from public CDNs (`jsdelivr`, `esm.sh`)
   break local development without any changes to Graphinate itself.
3. **Reproducibility & Security:** Strict zero-trust security postures forbid arbitrary script execution from unverified
   public CDNs in production or staging networks.

## Rationale

Evaluating the vendoring strategy against the **7 Council Pillars** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):

- **Symmetry (Noether):** The server routes already host local static web applications (`/static`, `/graphiql`, `/voyager`, `/viewer`). Serving viewer assets from `/static/vendor/` creates a uniform, self-contained hosting topology.
- **Falsifiability (Popper):** Offline operation is directly verifiable via unit and integration tests with disconnected network sockets or mocked HTTP blockers.
- **Efficiency (Shannon):** The total bundle size for the core 3D viewer assets (`3d-force-graph.min.js`, `tweakpane.min.js`, `@tweakpane/plugin-essentials.min.js`, `murmurhash3_gc.min.js`, `three.module.min.js`, `d3.min.js`) is ~2.3 MB uncompressed (~600 KB gzip/brotli wheel compression). This is lean enough to ship directly in the Python wheel without multi-megabyte external bloat.
- **Safety (The Golem):** Completely removes remote script injection risks and CDN tracking.
- **Clarity (Feynman):** Asset paths in `viewer/index.html` become clear local references (`/static/vendor/...`) instead of obscure versioned CDN endpoints.
- **Consistency (Russell):** Local static mounts (`Starlette` `StaticFiles`) manage both images and vendor scripts through the existing `paths_mapping['static']` mechanism.
- **Harmony (The Steward):** Preserves instantaneous, "works-out-of-the-box" local developer visualization.

## Specification

### 1. Vendored Asset Directory Layout

Vendored JavaScript dependencies will be stored in `src/graphinate/server/web/static/vendor/`:

```
src/graphinate/server/web/static/
├── images/
│   ├── logo-128.png
│   ├── logo.svg
│   └── network_graph.png
└── vendor/
    ├── 3d-force-graph.min.js
    ├── tweakpane.min.js
    ├── tweakpane-plugin-essentials.min.js
    ├── murmurhash3_gc.min.js
    ├── three.module.min.js
    └── d3.min.js
```

### 2. Static Route Serving

The existing Starlette router in `graphinate.server.starlette` mounts `paths_mapping['static']` at `/static`.
Vendored files are therefore available at:
- `/static/vendor/3d-force-graph.min.js`
- `/static/vendor/tweakpane.min.js`
- `/static/vendor/tweakpane-plugin-essentials.min.js`
- `/static/vendor/murmurhash3_gc.min.js`
- `/static/vendor/three.module.min.js`
- `/static/vendor/d3.min.js`

### 3. Viewer HTML Refactoring

In [`src/graphinate/server/web/viewer/index.html`](file:///C:/dev/erivlis/graphinate/src/graphinate/server/web/viewer/index.html), replace external CDN `<script>` and `<link>` tags with local absolute root paths:

```html
<!-- Local Vendored Dependencies -->
<script src="/static/vendor/murmurhash3_gc.min.js"></script>
<script src="/static/vendor/3d-force-graph.min.js"></script>
<script src="/static/vendor/d3.min.js"></script>

<script type="module">
    import * as Tweakpane from '/static/vendor/tweakpane.min.js';
    import * as TweakpaneEssentialsPlugin from '/static/vendor/tweakpane-plugin-essentials.min.js';
    import * as THREE from '/static/vendor/three.module.min.js';

    globalThis.Tweakpane = Tweakpane;
    globalThis.TweakpaneEssentialsPlugin = TweakpaneEssentialsPlugin;
    globalThis.THREE = THREE;
</script>
```

### 4. Wheel & Package Data Verification

Ensure `pyproject.toml` and packaging configurations include all non-Python assets (`*.js`, `*.css`, `*.html`, `*.png`, `*.svg`) within `graphinate/server/web`.

## Backwards Compatibility

- **Public API:** No changes to Python signatures (`server(...)`, `create_app(...)`, `GraphQLBuilder`).
- **Network Compatibility:** Fully backwards compatible; users who previously used the viewer online will now benefit from offline loading and faster startup times without external HTTP requests.

## How to Teach This / Documentation Plan

- Update [`docs/usage/cli.md`](file:///C:/dev/erivlis/graphinate/docs/usage/cli.md) and [`docs/development.md`](file:///C:/dev/erivlis/graphinate/docs/development.md) highlighting that the built-in 3D viewer is 100% offline-ready and works in air-gapped environments.

## Reference Implementation

- Asset directory: [`src/graphinate/server/web/static/vendor/`](file:///C:/dev/erivlis/graphinate/src/graphinate/server/web/static/vendor/)
- Viewer template: [`src/graphinate/server/web/viewer/index.html`](file:///C:/dev/erivlis/graphinate/src/graphinate/server/web/viewer/index.html)
- Server tests: [`tests/graphinate/renderers/test_graphql_server.py`](file:///C:/dev/erivlis/graphinate/tests/graphinate/renderers/test_graphql_server.py)

## Rejected Ideas

- **On-Demand CLI Asset Installer (`graphinate assets install`):**
  *Rejected.* An installer command requires network connectivity at setup time, failing the primary air-gap requirement. Shipping ~2.3 MB uncompressed (~600 KB compressed) directly in the package wheel provides a superior, zero-friction developer experience.
- **Vendoring GraphiQL and Voyager Full Bundles in GEP-019:**
  *Rejected for this proposal.* GraphiQL (with React/ReactDOM) and Voyager exceed 8 MB minified. The core visualization tool is the 3D Force-Directed Viewer (`/viewer`). GraphiQL and Voyager can remain optional or addressed in a subsequent proposal if full air-gappability for raw GraphQL IDEs is required.

## Open Questions

- [x] Should vendored scripts use relative (`./static/vendor/...`) or root-relative (`/static/vendor/...`) URLs?
  *Decision:* Root-relative (`/static/vendor/...`) because Starlette serves the viewer at `/viewer` and `/viewer/`, ensuring consistent resolution regardless of trailing slashes.

## Change Log

* **2025-12-25:** Initial draft proposing vendor vs. installer options.
* **2026-10-21:** Council review accepted Option 1 (in-package vendoring) for core 3D viewer assets; refactored proposal to adhere to PEP/EP standard and GEP-000.
* **2026-10-22:** Implemented in-package vendoring under `src/graphinate/server/web/static/vendor/`. Refactored `viewer/index.html` to eliminate all external CDN calls. Added regression test `test_offline_viewer_vendored_assets`. Status updated to `Active`.
