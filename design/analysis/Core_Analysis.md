# Graphinate Core Analysis

## Overview
This document analyzes the core utility modules in `graphinate` that support the main modeling and building logic.

## Modules

### 1. `color.py`
- **Role**: Handles color generation for nodes based on their types.
- **Key Logic**:
    - `node_color_mapping`: Generates a mapping of node IDs to RGBA colors using Matplotlib colormaps. It assigns colors based on node types.
    - `color_hex`: Converts RGB/RGBA tuples to Hex strings.
    - `convert_colors_to_hex`: Modifies a NetworkX graph in-place to convert color attributes to Hex.

### 2. `enums.py`
- **Role**: Defines the `GraphType` enum.
- **Key Logic**:
    - Maps enum members (`Graph`, `DiGraph`, etc.) to their corresponding NetworkX classes.
    - `GraphType.of(graph)`: Factory method to determine the enum type from an existing NetworkX graph instance.

### 3. `tools.py`
- **Role**: General utilities.
- **Key Logic**:
    - `utcnow()`: Returns the current time in UTC.

### 4. `typing.py`
- **Role**: Central repository for type hints and protocols.
- **Key Logic**:
    - Defines `Node`, `Edge`, `Element` types.
    - Defines Protocols (`Items`, `Nodes`, `Edges`) for generator functions.
    - Defines `GraphRepresentation` union type.

### 5. `constants.py`
- **Role**: Stores global constants.
- **Key Logic**:
    - `DEFAULT_NODE_DELIMITER`: Separator for node labels.
    - `DEFAULT_EDGE_DELIMITER`: Separator for edge labels.

### 6. `converters.py`
- **Role**: Data conversion and serialization utilities.
- **Key Logic**:
    - **Infinity Handling**: Maps `math.inf` to string representations for GraphQL compatibility.
    - **Label Conversion**: Formats tuples into string labels using delimiters.
    - **ID Encoding/Decoding**:
        - Uses `repr()` to stringify objects.
        - Encodes stringified objects to Base64.
        - Decodes Base64 and uses `ast.literal_eval` to reconstruct objects.
        - This mechanism is used to generate stable IDs for GraphQL nodes and edges.
