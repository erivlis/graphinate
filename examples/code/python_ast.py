"""
Define functions to create an abstract syntax tree (AST) graph model using the 'graphinate' library.
The 'ast_graph_model' function parses the AST of a specified class and creates nodes and edges for the graph model.
The nodes represent AST nodes with their type and label, while the edges represent relationships between AST nodes.
"""

import ast
import hashlib
import inspect
import operator
import pickle
import threading
import webbrowser
from _ast import AST
from collections.abc import Iterable
from tempfile import TemporaryDirectory

import graphinate


def _ast_nodes(parsed_asts: Iterable[AST]):
    for item in parsed_asts:
        if not isinstance(item, ast.Load):
            yield item
            yield from _ast_nodes(ast.iter_child_nodes(item))


def _ast_edge(parsed_ast: AST):
    for child_ast in ast.iter_child_nodes(parsed_ast):
        if not isinstance(child_ast, ast.Load):
            edge = {'source': parsed_ast, 'target': child_ast}
            edge_types = (
                field_name
                for field_name, value
                in ast.iter_fields(parsed_ast)
                if child_ast == value
                   or (child_ast in value if isinstance(value, list) else False)
            )
            edge_type = next(edge_types, None)
            if edge_type:
                edge['type'] = edge_type
            yield edge
            yield from _ast_edge(child_ast)


def ast_graph_model():
    """
    Create an abstract syntax tree (AST) graph model.

    Returns:
        GraphModel: A graph model representing the AST nodes and their relationships.
    """

    graph_model = graphinate.model(name='AST Graph')

    root_ast_node = ast.parse(inspect.getsource(graphinate.builders.D3Builder))

    def node_type(ast_node):
        return ast_node.__class__.__name__

    def node_label(ast_node) -> str:
        label = ast_node.__class__.__name__

        for field_name in ('name', 'id'):
            if field_name in ast_node._fields:
                value = operator.attrgetter(field_name)(ast_node)
                label = f"{label}\n{field_name}: {value}"

        return label

    def key(value):
        # noinspection InsecureHash
        return hashlib.shake_128(pickle.dumps(value)).hexdigest(20)

    def endpoint(value, endpoint_name):
        return key(value[endpoint_name])

    def source(value):
        return endpoint(value, 'source')

    def target(value):
        return endpoint(value, 'target')

    @graph_model.node(type_=node_type,
                      key=key,
                      label=node_label,
                      unique=True)
    def ast_node(**kwargs):
        yield from _ast_nodes([root_ast_node])

    @graph_model.edge(type_='edge',
                      source=source,
                      target=target,
                      label=operator.itemgetter('type'))
    def ast_edge(**kwargs):
        yield from _ast_edge(root_ast_node)

    return graph_model


def create_server(port: int, root_directory: str, open_browser: bool = True) -> threading.Thread:
    import http.server
    import socketserver

    url = f"http://localhost:{port}"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=root_directory, **kwargs)

    def serve():
        with socketserver.TCPServer(('', port), Handler) as httpd:
            print("Serving at:", url)
            httpd.serve_forever()

    server_thread = threading.Thread(target=serve)
    server_thread.daemon = True
    server_thread.start()

    if open_browser:
        webbrowser.open(url)


if __name__ == '__main__':
    ast_model = ast_graph_model()
    # schema = graphinate.builders.GraphQLBuilder(ast_model).build()
    # graphinate.graphql.server(schema)

    diagram = graphinate.builders.MermaidBuilder(ast_model).build(with_edge_labels=False)

    html_diagram = graphinate.mermaid.html(diagram)

    ## Save the HTML diagram to a file and serve it
    with TemporaryDirectory() as temp_dir:
        with open(f"{temp_dir}/index.html", 'w') as f:
            f.write(html_diagram)

        # Serve the HTML diagram
        create_server(port=8077, root_directory=temp_dir, open_browser=True)

        # Keep the main thread alive to allow the server to run
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Server stopped")
