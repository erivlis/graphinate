---
title: "GEP-020: Modular Frontend Architecture"
description: "The Graphinate Viewer is currently implemented as a single monolithic `index.html` file containing HTML, CSS, and"
icon: lucide/git-branch
status: draft
---

# GEP-020: Modular Frontend Architecture

| Field       | Value                         |
|:------------|:------------------------------|
| **GEP**     | 20                            |
| **Title**   | Modular Frontend Architecture |
| **Author**  | Eran Rivlis                   |
| **Delegate**| The Council                   |
| **Status**  | Draft                         |
| **Type**    | Standards Track               |
| **Created** | 2025-12-25                    |
| **Updated** | 2026-10-22                    |

## Abstract

The Graphinate Viewer is currently implemented as a single monolithic `index.html` file containing HTML, CSS, and
JavaScript. This proposal advocates for refactoring the frontend code into modular ES6 JavaScript files and adopting a
lightweight window management library to improve maintainability and readability.

## Motivation

**Issues:**

1. **Readability:** A 500+ line HTML file mixing three languages is hard to read.
2. **Maintainability:** Logic is tightly coupled. The custom "Floating Panel" implementation (drag/resize/stacking) is
   verbose and reinventing the wheel.
3. **Collaboration:** Harder to work on specific components (e.g., just the UI) without merge conflicts.

## Specification

### 1. File Structure

Refactor the code into the following structure:

```
src/graphinate/server/web/viewer/
├── index.html
├── css/
│   └── style.css
└── js/
    ├── main.js          # Entry point
    ├── graph.js         # ForceGraph3D logic
    ├── ui.js            # Tweakpane logic
    ├── panels.js        # Window management logic
    └── api.js           # GraphQL fetching logic
```

Update `index.html` to import the entry point:

```html

<script type="module" src="./js/main.js"></script>
```

### 2. Window Management (WinBox.js)

Replace the custom, imperative DOM manipulation code for floating panels with **WinBox.js**.

**Current:** 100+ lines of custom drag/resize/z-index logic.
**Proposed:**

```javascript
import WinBox from 'winbox/src/js/winbox.js'; // or vendor path

export function createPanel(title, url) {
    new WinBox(title, {
        url: url,
        class: "modern",
        x: "center",
        y: "center",
        width: "80%",
        height: "80%"
    });
}
```

**Benefits:**

* **Code Deletion:** Removes significant technical debt.
* **Features:** Adds minimize, maximize, fullscreen, and focus management out of the box.
* **Stability:** Relies on a battle-tested library.

## Backwards Compatibility

This is an internal refactoring of the frontend. No external API changes.
## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Clarity (Feynman):** Splitting monolithic inline JavaScript in `viewer/index.html` into ES modules makes frontend logic maintainable and readable.
- **Safety (The Golem):** Modular JS allows isolated testing of UI components (panels, graph controllers, themes).
- **Harmony (The Steward):** Retains standalone static hosting without requiring an external Node.js build step.

## Reference Implementation

- Viewer frontend modules: `src/graphinate/server/web/viewer/js/`

## Change Log

* **2025-12-26:** Initial draft.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment.
