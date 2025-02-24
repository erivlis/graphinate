import ast
import hashlib
import inspect
import operator
import pickle
import random
from _ast import AST
from collections.abc import Iterable

import faker
import pytest

import graphinate


@pytest.fixture
def country_count():
    return random.randint(1, 10)


@pytest.fixture
def city_count():
    return random.randint(20, 40)


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


@pytest.fixture
def ast_graph_model():
    graph_model = graphinate.model(name='AST Graph')

    root_ast_node = ast.parse(inspect.getsource(graphinate.builders.D3Builder))

    def node_type(ast_node):
        return ast_node.__class__.__name__

    def node_label(ast_node) -> str:
        label = ast_node.__class__.__name__

        for field_name in ('name', 'id'):
            if field_name in ast_node._fields:
                label = f"{label}\n{field_name}: {operator.attrgetter(field_name)(ast_node)}"

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

    @graph_model.node(type_=node_type, key=key, label=node_label, unique=True)
    def ast_node(**kwargs):
        yield from _ast_nodes([root_ast_node])

    @graph_model.edge(type_='edge', source=source, target=target, label=operator.itemgetter('type'))
    def ast_edge(**kwargs):
        yield from _ast_edge(root_ast_node)

    return graph_model


@pytest.fixture
def map_graph_model(country_count, city_count):
    country_ids = {str(c): None for c in range(1, country_count + 1)}
    city_ids = {str(c): random.choice(list(country_ids.keys())) for c in range(1, city_count + 1)}

    graph_model = graphinate.model(name='Map')

    faker.Faker.seed(0)
    fake = faker.Faker()

    def country_node_label(value):
        return fake.country()

    def city_node_label(value):
        return fake.city()

    @graph_model.node(label=country_node_label, unique=False)
    def country(country_id=None, **kwargs):

        if country_id and country_id in country_ids:
            yield country_id
        else:
            yield from country_ids

    @graph_model.node(parent_type='country', label=city_node_label, unique=False)
    def city(country_id=None, city_id=None, **kwargs):

        if country_id is None and city_id is None:
            yield from city_ids.keys()

        if country_id is None and city_id is not None and city_id in city_ids:
            yield city_id

        if city_id is not None and country_id is not None and city_ids.get(city_id) == country_id:
            yield city_id

        if country_id is not None and city_id is None:
            yield from (k for k, v in city_ids.items() if v == country_id)

    @graph_model.node(type_=operator.itemgetter('sex'),
                      parent_type='city',
                      unique= False,
                      key=operator.itemgetter('username'),
                      label=operator.itemgetter('name'))
    def person(country_id=None, city_id=None, person_id=None, **kwargs):
        yield fake.profile()

    return country_count, city_count, graph_model


@pytest.fixture
def octagonal_graph_model():
    graph_model = graphinate.model(name="Octagonal Graph")
    number_of_sides = 8

    # Register edges supplier function
    @graph_model.edge()
    def edge():
        for i in range(number_of_sides):
            yield {'source': i, 'target': i + 1}
        yield {'source': number_of_sides, 'target': 0}

    return graph_model


@pytest.fixture
def graphql_query():
    return """
    query Graph {
      graph {
        name
        nodeTypeCounts {
          name
          value
        }
        edgeTypeCounts {
          name
          value
        }
        created
        nodeCount
        edgeCount
        size
        order
        radius
        diameter
        averageDegree
        hash
      }
      nodes {
        id
        ...ElementDetails
        neighbors {id type label}
        children: neighbors(children: true) {id type label}
        edges {id type label}
      }
      edges {
        source {id ...ElementDetails}
        target {id ...ElementDetails}
        ...ElementDetails
        weight
      }
    }

    fragment ElementDetails on GraphElement {
      label
      type
      label
      color
      created
      updated
    }
    """
