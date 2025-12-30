# Graphinate Viewer Grading

This document evaluates the `graphinate.server.web.viewer` (Frontend) against the **Council Framework** values.

## 1. `index.html`

*   **Efficiency (Shannon):** 5/5.
    *   Zero build step.
    *   No `node_modules` bloat in the Python package.
    *   Uses ES Modules efficiently.
*   **Safety (The Golem):** 2/5.
    *   **External Dependencies:** Relies on public CDNs (`esm.sh`, `jsdelivr`). If these go down or change, the viewer breaks. It also requires an internet connection to work (cannot run offline/air-gapped).
    *   **Security:** Loading scripts from third-party CDNs introduces a potential supply chain risk (though integrity hashes are used for some).
*   **Clarity (Feynman):** 3/5.
    *   The code is monolithic (one big file).
    *   Mixing HTML, CSS, and JS makes it harder to read.
    *   The "Floating Panel" logic is verbose and DOM-heavy.
*   **Symmetry (Noether):** 4/5.
    *   The UI controls map directly to the graph parameters.
*   **Harmony (The Steward):** 4/5.
    *   It integrates well with the backend via GraphQL.

## Overall Assessment

The viewer is a marvel of pragmatism. By avoiding a complex JS build chain (Webpack/React), it keeps the Python library lightweight and easy to distribute. However, the reliance on CDNs is a major "Safety" violation for a library that might be used in enterprise/offline environments.

## Recommendations (The Dennis Point)

1.  **Vendor Dependencies:** Download the JS libraries and bundle them with the package to allow offline usage and ensure stability.
2.  **Modularize:** Even without a build step, the JS code can be split into separate `.js` files and imported via `<script type="module" src="...">`.
