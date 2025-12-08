## v0.12.0 (2025-12-09)

### Feat

- enhance D3 JSON output by converting datetime, timedelta, and bytes.

## v0.11.1 (2025-12-05)

### Fix

- **builders**: update attribute reference to `__strawberry_definition__` for enum values
- **color**: handle single-element color arrays and ensure consistent output type

### Refactor

- streamline imports in `__init__.py` for consistency and clarity

## v0.11.0 (2025-11-30)

### Feat

- Adds numpy, configures MyPy type checking and Commitizen.

### Fix

- **visibility_graph**: Simplifies type hints using T | None syntax.
- **tests**: Updates CI to run pytest tests sequentially.

### Refactor

- Abstracts `Builder`, refines typing, and improves GraphQL value resolution.
- Optimizes node color mapping with NumPy and refines default type logic.
- Refactors documentation into dedicated pages and updates image attributes.

## v0.10.1 (2025-11-17)

## v0.10.0 (2025-11-17)

## v0.9.0 (2025-11-02)

## v0.8.6 (2025-08-31)

### Feat

- add networkx-query dependency for enhanced graph querying capabilities
- enhance documentation and configuration for mkdocs and add new plugins

### Fix

- adjust node value in graph parameters for improved visualization
- update Python version in CI configuration to 3.14.0-alpha.7
- update pytest dependencies in CI configuration files
- clean up README.md by removing extra newlines and improving formatting
- update node_link_data call to specify nodes and edges parameters in builders.py
- update external library links to use jsDelivr CDN and upgrade graphql-voyager to version 2.1.0

### Refactor

- update docstring for UniverseNode
- move `favicon_route` import to the top of `__init__.py` for consistency
- remove OpenTelemetryExtension from GraphQL schema and add docstring to `_graphql_app` function
- introduce TypeAlias for NodeTuple and EdgeTuple; update type hints for clarity
- rename acknowledge.md to acknowledgements.md and intro.md to introduction.md; update links for consistency
- replace None with NoneType for UniverseNode definition
- update type hints to use union syntax for optional types
- update type hints to use union syntax for optional types
- update graph model name to include code object qualifier in python_ast.py

## v0.8.5 (2025-04-05)

### Feat

- add color conversion to hex for graph nodes and update documentation
- add optional title parameter to build method for Mermaid diagrams
- add values_format option to build method for flexible output formats

### Fix

- downgrade version from 0.8.6 to 0.8.5 in graphql.py and pyproject.toml
- update networkx-mermaid dependency to remove version constraint

### Refactor

- reorganize GraphQL code section for improved readability
- update parameter documentation from 'Parameters' to 'Args' for consistency

## v0.8.4 (2025-03-24)

### Feat

- add option to exclude edge labels in Mermaid diagram builder

## v0.8.3 (2025-03-20)

### Fix

- update script sources to use jsDelivr and instantiate ForceGraph3D correctly

### Refactor

- instantiate graph model for CLI serving
- update imports and improve graph building process

## v0.8.2 (2025-03-20)

## v0.8.1 (2025-03-12)

### Refactor

- improve encoding and decoding functions for graph node IDs
- simplify temporary directory handling in git_commits and add Mermaid materializer

## v0.8.0 (2025-03-08)

### Fix

- correct spelling of "Graphinate" in documentation and update image height

### Refactor

- reorganize imports and update GraphQL function to server

## v0.7.0 (2025-02-25)

## v0.6.0 (2025-02-17)

## v0.5.1 (2025-02-13)

## v0.5.0 (2025-02-09)

## v0.4.0 (2025-01-29)

## v0.3.2 (2025-01-27)

## v0.3.1 (2024-10-17)

## v0.3.0 (2024-06-28)

## v0.2.21 (2024-05-09)

## v0.2.20 (2024-04-04)

## v0.2.19 (2024-03-27)

## v0.2.18 (2024-03-23)

## v0.2.17 (2024-03-13)

## v0.2.16 (2024-02-28)

## v0.2.15 (2024-02-24)

## v0.2.14 (2024-02-24)

## v0.2.13 (2024-02-24)

## v0.2.12 (2024-02-08)

## v0.2.11 (2024-01-27)

## v0.2.10 (2023-12-19)

## v0.2.9 (2023-12-14)

## v0.2.8 (2023-11-27)

## v0.2.7 (2023-10-26)

## v0.2.6 (2023-10-15)

## v0.2.5 (2023-10-05)

## v0.2.4 (2023-10-04)

## v0.2.3 (2023-09-27)

## v0.2.1 (2023-09-27)

## v0.2.0 (2023-09-24)

## v0.1.1 (2023-09-23)

## v0.1.0 (2023-09-22)

## v0.0.9 (2023-08-20)

## v0.0.8 (2023-08-19)

## v0.0.7 (2023-08-16)

## v0.0.6 (2023-08-14)

## v0.0.5 (2023-08-14)
