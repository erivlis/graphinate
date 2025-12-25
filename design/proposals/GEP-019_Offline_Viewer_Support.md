# GEP-019: Offline Viewer Support

| Field       | Value                  |
|:------------|:-----------------------|
| **GEP**     | 19                     |
| **Title**   | Offline Viewer Support |
| **Author**  | Eran Rivlis            |
| **Status**  | Draft                  |
| **Type**    | Standards Track        |
| **Created** | 2025-12-25             |

## Abstract

The current Graphinate Viewer relies on external CDNs (esm.sh, jsdelivr) to load JavaScript libraries. This prevents the
viewer from functioning in offline or air-gapped environments and introduces external points of failure. This proposal
advocates for vendoring these dependencies or providing a mechanism to host them locally.

## Motivation

**Issues:**

1. **Offline Usage:** Users without internet access cannot view the graph.
2. **Stability:** Changes or outages in the CDN providers break the viewer.
3. **Security:** Loading code from third parties is a security risk in some environments.

## Specification

### Option 1: Vendor in Package (Preferred for small libs)

Download the minified JS files and distribute them within the `graphinate` Python package.

* `src/graphinate/server/web/static/vendor/3d-force-graph.min.js`
* `src/graphinate/server/web/static/vendor/tweakpane.min.js`

### Option 2: Asset Installer Command

To avoid bloating the PyPI package size, include a CLI command to download assets.

```bash
graphinate assets install
```

This command would fetch the specific versions of the libraries and save them to the user's local configuration or the
package directory.

### Implementation

Update `index.html` to use relative paths:

```html

<script src="./static/vendor/3d-force-graph.min.js"></script>
```

## Backwards Compatibility

This is purely additive. We can fallback to CDN if local files are missing, or make it the default.
