# GEP-028: MCP Server Integration

| Field       | Value                  |
|:------------|:-----------------------|
| **GEP**     | 28                     |
| **Title**   | MCP Server Integration |
| **Author**  | Eran Rivlis            |
| **Status**  | Draft                  |
| **Type**    | Standards Track        |
| **Created** | 2026-01-01             |
| **Updated** | 2026-01-01             |

## Abstract

This proposal advocates for exposing Graphinate as a **Model Context Protocol (MCP) Server**. This will allow Large Language Models (LLMs) like Claude and ChatGPT to interact with Graphinate directly—building graphs from unstructured text, querying graph structures, and generating visualizations.

## References

*   **Official Docs:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)
*   **Python SDK:** [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)

## Motivation

LLMs excel at processing unstructured text but struggle with maintaining complex structural relationships (graphs) in their context window. They often "hallucinate" connections or lose track of long chains of dependencies.

**Graphinate as an MCP Server solves this by:**
1.  **Offloading Structure:** The LLM can push entities and relationships into Graphinate.
2.  **Grounding:** The LLM can query the graph ("What is connected to X?") to ground its answers in fact.
3.  **Visualization:** The LLM can request a visual representation of its current context.

## Architectural Challenge: Push vs Pull

Graphinate is architected around **Generators** (Pull model). The engine iterates over a generator to discover nodes.
MCP Tools are **Function Calls** (Push model). The LLM calls a function to add data.

**Solution: The Async Queue Generator**
We will bridge this gap by treating the MCP interface as an **Async Data Source**.

1.  The MCP Server initializes a `GraphModel`.
2.  It registers a `@model.node()` generator that yields from an `asyncio.Queue`.
3.  The MCP Tools (`add_node`) simply push data into this queue.
4.  The `GraphEngine` (GEP-024) consumes the queue in realtime, updating the graph.

## Specification

We will implement an MCP Server using the `mcp` Python SDK. This will be an optional integration (`graphinate[mcp]`).

### 1. Tools (The Actions)

The server will expose the following tools to the LLM:

*   **`graph_ingest_node(id: str, type: str, attributes: dict)`**: Pushes a node payload to the ingestion queue.
*   **`graph_ingest_edge(source: str, target: str, type: str, attributes: dict)`**: Pushes an edge payload to the ingestion queue.
*   **`graph_get_neighbors(id: str)`**: Queries the built graph for neighbors.
*   **`graph_shortest_path(source: str, target: str)`**: Finds the path between two nodes.
*   **`graph_render(format: str = 'html')`**: Returns a visualization (HTML snippet or Image URL) of the current graph.

### 2. Resources (The Data)

The server will expose resources for direct reading:

*   **`graph://summary`**: A text summary of the graph (node counts, density, types).
*   **`graph://schema`**: The GraphQL schema definition.
*   **`graph://export/json`**: The full graph in JSON format.

### 3. Prompts (The Templates)

We can provide pre-defined prompts to help the user:

*   **"Visualize this text"**: A prompt that instructs the LLM to extract entities from the user's selection and call `graph_ingest_node`/`graph_ingest_edge`.

## Architecture Implementation

```python
# graphinate/mcp/server.py
import asyncio
from mcp.server import Server

class GraphinateMCPServer:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.model = graphinate.model(name="MCP Graph")
        
        # Define the generator that consumes the queue
        @self.model.node()
        async def mcp_source():
            while True:
                item = await self.queue.get()
                yield item
                
        self.engine = GraphEngine(self.model)
        # Start the engine in a background task
        
    async def handle_ingest_node(self, id, type, attributes):
        # Push to the queue, which the Engine consumes
        await self.queue.put({"id": id, "type": type, **attributes})
```

## Integration

This fits into **Layer 4 (Integrations)** of the Modularization Strategy (GEP-002).

*   **Package:** `graphinate`
*   **Extra:** `mcp`
*   **Dependencies:** `mcp` (Model Context Protocol SDK).

## Use Cases

1.  **Code Analysis:** "Read this repo and build a dependency graph."
2.  **Knowledge Graph:** "Extract all people and companies from this article."
3.  **Debugging:** "Visualize the call stack I just pasted."
