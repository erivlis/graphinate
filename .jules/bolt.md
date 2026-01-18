## 2026-01-18 - Hoisting invariants in NetworkxBuilder
**Learning:** Hoisting `_parent_node_id` calculation and `node_types` counter lookup outside the node generation loop in `NetworkxBuilder._populate_nodes` significantly improves performance (approx 11% faster for nested graphs).
**Action:** When implementing builders with tight loops, identify and hoist invariant calculations and dictionary lookups.
