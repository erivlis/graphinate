## 2026-01-14 - NetworkX Builder Optimization
**Learning:** Hoisting invariant calculations (`_parent_node_id`) out of nested loops and using EAFP (`try-except`) for dictionary lookups in `NetworkxBuilder` yielded a 10x microbenchmark speedup.
**Action:** Look for invariant calculations in `builder` loops and prioritize EAFP for dictionary lookups in hot paths.
