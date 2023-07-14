import ast
import inspect
from _ast import AST
from typing import Iterable

import networkx as nx

import graphinate
from graphinate.plot import show


def _ast_nodes(parsed_asts: Iterable[AST]):
    for item in parsed_asts:
        yield item
        yield from _ast_nodes(ast.iter_child_nodes(item))


def _ast_edge(parsed_ast: AST):
    for child_ast in ast.iter_child_nodes(parsed_ast):
        yield {'source': parsed_ast, 'target': child_ast}
        yield from _ast_edge(child_ast)


graph_model = graphinate.GraphModel(name='AST')

root_ast_node = ast.parse(inspect.getsource(graphinate.graphs.D3Graph))


def node_label(ast_node) -> str:
    return f"{ast_node.__class__.__name__}: {tuple(ast.iter_fields(ast_node))}"


# @graph_model.node()
def ast_node():
    yield from _ast_nodes([root_ast_node])


@graph_model.edge()
def ast_edge():
    yield from _ast_edge(root_ast_node)


if __name__ == '__main__':
    # parsed_asts = [ast.parse(inspect.getsource(graphinate.modeling))]
    # for node in _ast_nodes(parsed_asts):
    #     node_type = node.__class__.__name__
    #     node_value = tuple(ast.iter_fields(node))
    #     print(node_type, node_value, sep=": ")

    networkx_graph = graphinate.graphs.NetworkxGraph(graph_model)

    # params = {
    #     'user_id': 'erivlis',
    #     'repository_id': 'graphinate',
    #     # 'user_id': 'andybrewer',
    #     # 'repository_id': 'operation-go',
    #     # 'commit_id': None,
    #     'file_id': 'README.md',
    #     # 'user_id' "strawberry-graphql"
    # }
    nx_graph: nx.Graph = networkx_graph.build()

    show(nx_graph)
