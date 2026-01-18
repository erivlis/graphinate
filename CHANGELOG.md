## v0.13.0 (2026-01-18)

### Feat

- make NumPy an optional dependency for color mapping.
- expose graph properties as read-only; clarify node generator argument rules.

### Refactor

- move Multiplicity enum, modernize type hints, and simplify logic.
- align GraphModel import path with package structure.
- streamline engine imports for builder module rename.
- rename builder modules by removing leading underscores.

### Perf

- Cache namedtuple class creation in modeling.py (#35)
- optimize Counter updates in NetworkX builder

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

### Fix

- Unifies node and edge attribute rectification logic.
- Refactors `test_save_model_reference` for robustness and clarity.

### Refactor

- Extracts graph building logic into dedicated private methods.
- Enhances viewer performance, updates dependencies, and refines styling.

## v0.10.0 (2025-11-17)

### Feat

- Introduces `GraphNodeType` enum to filter neighbors by type.
- Generalizes AST parsing to use `code_object` instead of fixed source.
- Adds example docstring and refactors plotting module path.

### Fix

- Fixes Sonar issues by validating save paths and confirming overwrites.

### Refactor

- Relaxes dependency versions.

## v0.9.0 (2025-11-02)

### Feat

- ci: add CI workflow for testing and linting across multiple Python versions
- ci: Adds Python 3.14 to CI for testing/linting; updates actions.

### Fix

- chore: update test dependencies in CI configuration to include httpx

### Refactor

- Refactors Starlette module import paths by removing `__init__`.
- Updates documentation CI to use uv dependency groups.
- Applies formatting, adds type hints, and update GraphQL IDEs.

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

### Fix

- update test beta workflow

### Refactor

- refactor + updates

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

### Fix

- restore timezone compatibility with python 3.10

### Refactor

- update examples
- refactor + update tests
- update docs
- add system example - file tree
- add code examples - html dom - tokens
- add music example
- update GraphModel + NetworkxBuilder
- update viewer

## v0.6.0 (2025-02-17)

### Refactor

- update test
- update viewer - add advanced controls
- update NetworkxBuilder
- update viewer - improve styling and z-index handling + more
- update viewer - add color update functionality - add tools section to control panel
- updates - docs and readme improvements - fix rapidoc integrity ref
- update GitHub actions

## v0.5.1 (2025-02-13)

### Refactor

- bump to version 0.5.1

## v0.5.0 (2025-02-09)

### Feat

- add logo.svg

### Refactor

- update GraphModel + builders
- update viewer - add legend - add turn on/off node by types - update web dependencies
- update examples
- refactor viewer/index.html
- update math example

## v0.4.0 (2025-01-29)

### Refactor

- update readme
- update GitHub actions
- corrections
- minor change
- update docs
- remove tkinter based GUI + bump version to 0.4.0 - moved GUI Graph Atlas example - reformating - refactoring - improvements, fixes, and cleanup

## v0.3.2 (2025-01-27)

### Refactor

- update formating + refactoring + misc improvements and fixes
- move static/scripts to static/js
- refactor gui code
- update examples requirements files
- minor update
- update test beta GitHub Action
- remove Sonar GitHub action
- add GraphType.of() class method
- add Sonar GitHub action

## v0.3.1 (2024-10-17)

### Feat

- add python 3.13

### Refactor

- update test actions
- update test-beta.yml
- Update STATS.md
- update readme
- update test action
- update gitignore
- update beta test action
- updates

## v0.3.0 (2024-06-28)

### Refactor

- deprecate support for python 3.9 - update dependencies - Development Status set to: 4 - Beta
- update docstrings

## v0.2.21 (2024-05-09)

### Refactor

- update dependencies

## v0.2.20 (2024-04-04)

### Refactor

- update examples

## v0.2.19 (2024-03-27)

### Refactor

- update examples
- update html files

## v0.2.18 (2024-03-23)

### Refactor

- update test workflow
- updates
- update tests

## v0.2.17 (2024-03-13)

### Refactor

- updates
- update to actions/setup-python@v5
- update docs

## v0.2.16 (2024-02-28)

### Refactor

- update actions
- updates

## v0.2.15 (2024-02-24)

### Refactor

- add tests
- updates

## v0.2.14 (2024-02-24)

### Fix

- security update

## v0.2.13 (2024-02-24)

### Refactor

- update dependencies + misc improvements
- update examples
- update docs

## v0.2.12 (2024-02-08)

### Refactor

- updates

## v0.2.11 (2024-01-27)

### Refactor

- Update pyproject.toml

## v0.2.10 (2023-12-19)

### Refactor

- bump version to 0.2.10

## v0.2.9 (2023-12-14)

### Refactor

- bump version 0.2.9

## v0.2.8 (2023-11-27)

### Fix

- handle tkinter OS-specific wm_attributes correctly

### Refactor

- update dependencies

## v0.2.7 (2023-10-26)

### Refactor

- updates

## v0.2.6 (2023-10-15)

### Feat

- add support for Python 3.12

### Refactor

- refactoring
- update dependencies
- Create dependabot.yml
- [ImgBot] Optimize images
- update docs
- Update README.md
- add python_dependencies example
- update docs

## v0.2.5 (2023-10-05)

### Refactor

- update logo

## v0.2.4 (2023-10-04)

### Refactor

- update typing and docs
- update publish-docs GitHub workflow
- test python 3.12
- update requirements
- update docs
- updates
- updates
- updates tests
- updates
- update GitHub test workflow
- refactoring
- update README.md

## v0.2.3 (2023-09-27)

### Refactor

- update docs - add examples to docs - correct and improve docstrings
- Update README.md add page links screenshot
- update docs - add examples to docs - correct and improve docstrings
- Update README.md
- update builders tests
- update docs
- update tests

## v0.2.1 (2023-09-27)

### Refactor

- update tests

## v0.2.0 (2023-09-24)

### Refactor

- update docs
- update tests - refactoring - update docs - add codecov
- Update README.md
- Update pyproject.toml

## v0.1.1 (2023-09-23)

### Refactor

- update docs
- update actions
- updates

## v0.1.0 (2023-09-22)

### Refactor

- updates
- update readme
- update readme + docs
- Update README.md
- refactoring + docs updates
- updates
- updates + refactoring
- improvements
- update README.md + docs

## v0.0.9 (2023-08-20)

### Refactor

- update README.md + Docs + refactoring

## v0.0.8 (2023-08-19)

### Feat

- add Mutation refresh operation to GraphQLBuilder

### Refactor

- Update pyproject.toml
- update README.md
- update graph_atlas.py
- updates

## v0.0.7 (2023-08-16)

### Feat

- add cli commands

### Refactor

- update README.md
- update GitHub workflow
- updates linting fixes
- update README.md + docs
- update README.md + docs
- Create codeql.yml

## v0.0.6 (2023-08-14)

### Refactor

- update GitHub workflows
- add docs
- refactor

## v0.0.5 (2023-08-14)

- initial implementation
