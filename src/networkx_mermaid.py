"""
The `networkx_mermaid.py` script defines a function to materialize a NetworkX graph as a Mermaid flowchart.
 It includes enumerations for graph orientation, node shapes, and output formats.
  The script also provides an example of generating a Mermaid diagram and serving it via a temporary HTTP server.
"""

from enum import Enum
from tempfile import TemporaryDirectory
from typing import TypeVar

import networkx as nx

MermaidGraph = TypeVar('MermaidGraph', bound='str')

class Orientation(Enum):
    """
    Orientation of a Mermaid graph.
    """
    TOP_DOWN = "TD"
    BOTTOM_UP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class NodeShape(Enum):
    """
    Shapes of a Mermaid graph node.
    """
    DEFAULT = ('(', ')')
    RECTANGLE = ('[', ']')
    ROUND_RECTANGLE = ('([', '])')
    SUBROUTINE = ('[[', ']]')
    DATABASE = ('[(', ')]')
    CIRCLE = ('((', '))')
    DOUBLE_CIRCLE = ('(((', ')))')
    FLAG = ('>', ']')
    DIAMOND = ('{', '}')
    HEXAGON = ('{{', '}}')
    PARALLELOGRAM = ('[/', '/]')
    PARALLELOGRAM_ALT = ('[\\', '\\]')
    TRAPEZOID = ('[/', '\\]')
    TRAPEZOID_ALT = ('[\\', '/]')


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <link rel="icon" type="image/x-icon" href="https://mermaid.js.org/favicon.ico">
    <meta charset="utf-8">
    <title>Mermaid Diagram</title>
    <style>
    pre.mermaid {
      font-family: "Fira Mono", "Roboto Mono", "Source Code Pro", monospace;
    }
    </style>
  </head>
  <body>
    <pre class="mermaid">
    </pre>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
      let config = { startOnLoad: true, flowchart: { useMaxWidth: false, htmlLabels: true } };
      mermaid.initialize(config);
    </script>
  </body>
</html>
"""


def edge_label(data: dict) -> str:
    label = data.get('label')
    return f"|{label}|" if label else ""


def contrast_color(color: str) -> str:
    """
    Return black or white by choosing the best contrast to input color

    Args:
        color: str - hex color code

    Returns:
        color: str - hex color code
    """
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return '#000000' if (r * 0.299 + g * 0.587 + b * 0.114) > 186 else '#ffffff'


def style(node_id: str, data: dict) -> str:
    color = data.get('color')
    return f"\nstyle {node_id} fill:{color}, color:{contrast_color(color)}" if color else ""


def title(graph: nx.Graph) -> str:
    return f"title: {graph.name}\n" if graph.name else ""


def mermaid(graph: nx.Graph,
            orientation: Orientation = Orientation.LEFT_RIGHT,
            node_shape: NodeShape = NodeShape.DEFAULT) -> MermaidGraph:
    """
    Materialize a graph as a Mermaid flowchart.

    Parameters
    ----------
    graph : nx.Graph
        A NetworkX graph.
    orientation : Orientation, optional
        The orientation of the graph, by default Orientation.LEFT_RIGHT.
    node_shape : NodeShape, optional
        The shape of the nodes, by default NodeShape.DEFAULT.

    Returns
    -------
    str
        A string representation of the graph as a Mermaid graph.
    """
    layout = 'dagre'
    look = 'neo'
    theme = 'neutral'
    config = (f"---\n"
              f"{title(graph)}"
              f"config:\n"
              f"  layout: {layout}\n"
              f"  look: {look}\n"
              f"  theme: {theme}\n"
              f"---")

    bra, ket = node_shape.value
    nodes = '\n'.join(
        f"{u}{bra}{v.get('label', u)}{ket}{style(u, v)}" for u, v in
        graph.nodes.data()
    )
    edges = '\n'.join(
        f"{u} -->{edge_label(d)} {v}" for u, v, d in graph.edges.data()
    )

    return (f"{config}\n"
            f"graph {orientation.value}\n"
            f"{nodes}\n"
            f"{edges}")


def markdown(diagram: str, title: str | None = None) -> str:
    output = f"```mermaid\n{diagram}\n```"
    if title:
        output = f"## {title}\n\n{output}"
    return output


def html(diagram: str, title: str | None = None) -> str:
    output = HTML_TEMPLATE.replace('<pre class="mermaid">', f'<pre class="mermaid">\n{diagram}\n')
    if title:
        output = output.replace('<title>Mermaid Diagram</title>', f'<title>{title}</title>')
    return output


if __name__ == '__main__':
    # colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF']
    pastel_colors = ['#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC', '#CCFFFF', '#FFCCFF']
    graphs: list[nx.Graph] = [nx.tetrahedral_graph(), nx.dodecahedral_graph()]

    for i, g in enumerate(graphs):
        nx.set_node_attributes(g, {n: {'color': pastel_colors[i]} for n in g.nodes})

    graph: nx.Graph = nx.disjoint_union_all(graphs)

    graph.name = ' + '.join(g.name for g in graphs)

    mermaid_diagram = mermaid(graph,
                              orientation=Orientation.LEFT_RIGHT,
                              node_shape=NodeShape.ROUND_RECTANGLE)

    with TemporaryDirectory() as temp_dir:
        with open(f"{temp_dir}/index.html", 'w') as f:
            rendered = html(mermaid_diagram, title=graph.name)
            f.write(rendered)

        import http.server
        import socketserver

        PORT = 8073


        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=temp_dir, **kwargs)


        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()
