import ast
import inspect
import operator
from _ast import AST
from typing import Iterable

import networkx as nx

import graphinate
from graphinate.plot import show


def _ast_nodes(parsed_asts: Iterable[AST]):
    for item in parsed_asts:
        if not isinstance(item, ast.Load):
            yield item
            yield from _ast_nodes(ast.iter_child_nodes(item))


def _ast_edge(parsed_ast: AST):
    for child_ast in ast.iter_child_nodes(parsed_ast):
        if not isinstance(child_ast, ast.Load):
            yield {'source': parsed_ast, 'target': child_ast}
            yield from _ast_edge(child_ast)


graph_model = graphinate.GraphModel(name='AST')

root_ast_node = ast.parse(inspect.getsource(graphinate.graphs.D3Graph))


def node_label(ast_node) -> str:
    label = ast_node.__class__.__name__

    for field_name in ('name', 'id'):
        if field_name in ast_node._fields:
            label = f"{label}\n{field_name}: {operator.attrgetter(field_name)(ast_node)}"

    return label


@graph_model.node(label=node_label, uniqueness=True)
def ast_node(**kwargs):
    yield from _ast_nodes([root_ast_node])


@graph_model.edge(label=str)
def ast_edge(**kwargs):
    yield from _ast_edge(root_ast_node)


if __name__ == '__main__':
    # Strawberry GraphQL Graph object
    gql_graph = graphinate.graphs.GraphqlGraph(graph_model)

    graphql_graph = gql_graph.build()

    # NetworkX Graph
    networkx_graph = graphinate.graphs.NetworkxGraph(graph_model)

    nx_graph: nx.Graph = networkx_graph.build()

    show(nx_graph)
