import ast
import inspect
import operator
from _ast import AST
from collections.abc import Iterable

import graphinate
import graphinate.builders


def _ast_nodes(parsed_asts: Iterable[AST]):
    for item in parsed_asts:
        if not isinstance(item, ast.Load):
            yield item
            yield from _ast_nodes(ast.iter_child_nodes(item))


def _ast_edge(parsed_ast: AST):
    for child_ast in ast.iter_child_nodes(parsed_ast):
        if not isinstance(child_ast, ast.Load):
            edge = {'source': parsed_ast, 'target': child_ast}
            edge_types = (field_name for field_name, value in ast.iter_fields(parsed_ast) if
                          child_ast == value or (child_ast in value if isinstance(value, list) else False))
            edge_type = next(edge_types, None)
            if edge_type:
                edge['type'] = edge_type
            yield edge
            yield from _ast_edge(child_ast)


def ast_graph_model():
    graph_model = graphinate.GraphModel(name='AST Graph')

    root_ast_node = ast.parse(inspect.getsource(graphinate.builders.D3Builder))

    def node_type(ast_node):
        return ast_node.__class__.__name__

    def node_label(ast_node) -> str:
        label = ast_node.__class__.__name__

        for field_name in ('name', 'id'):
            if field_name in ast_node._fields:
                label = f"{label}\n{field_name}: {operator.attrgetter(field_name)(ast_node)}"

        return label

    @graph_model.node(_type=node_type, label=node_label, uniqueness=True)
    def ast_node(**kwargs):
        yield from _ast_nodes([root_ast_node])

    @graph_model.edge(_type='edge', label=operator.itemgetter('type'))
    def ast_edge(**kwargs):
        yield from _ast_edge(root_ast_node)

    return graph_model


if __name__ == '__main__':
    ast_model = ast_graph_model()
    graphinate.materialize(ast_model)
