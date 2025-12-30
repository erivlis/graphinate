# Graphinate CLI Analysis

## Overview
The `graphinate.cli` module implements the Command Line Interface using the `click` library.

## Key Features

### 1. Dynamic Model Loading
- **Function**: `import_from_string`
- **Logic**: Parses a string like `module:variable`, imports the module, and retrieves the `GraphModel` instance. This allows the CLI to work with any user-defined model without hardcoding.

### 2. Commands
- **`save`**:
    - Builds the graph using `D3Builder`.
    - Serializes it to a JSON file.
    - Enforces safety checks (no absolute paths, no subdirectories).
- **`server`**:
    - Builds a GraphQL schema using `GraphQLBuilder`.
    - Starts a web server using `graphql.server`.
    - Displays an ASCII banner.

### 3. Argument Parsing
- **Logic**: `_get_kwargs` extracts arbitrary `--key=value` arguments from the command line and passes them to the builders/server. This allows passing dynamic configuration to the underlying components.
