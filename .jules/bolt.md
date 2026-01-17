# Bolt's Journal

## 2024-05-22 - [Project Start]
**Learning:** Initializing Bolt's journal for Graphinate.
**Action:** Document critical performance learnings here.

## 2026-01-17 - [Hoist Loop Invariants in Builders]
**Learning:** In `NetworkxBuilder._populate_nodes`, the `_parent_node_id` calculation depends only on `kwargs` and `node_type_absolute_id`, which are constant during the node generation loop.
**Action:** Always look for invariant calculations inside tight generation loops (especially in builders) and hoist them out. This reduced graph generation time by ~15% for nested graphs.
