import random

import graphinate
import pytest


@pytest.fixture()
def country_count():
    return random.randint(1, 10)


@pytest.fixture()
def city_count():
    return random.randint(20, 40)


@pytest.fixture()
def map_graph_model(country_count, city_count):
    country_ids = {str(c): None for c in range(1, country_count + 1)}
    city_ids = {str(c): random.choice(list(country_ids.keys())) for c in range(1, city_count + 1)}

    graph_model = graphinate.GraphModel(name='Map')

    @graph_model.node()
    def country(country_id=None, **kwargs):

        if country_id and country_id in country_ids:
            yield country_id
        else:
            yield from country_ids

    @graph_model.node(parent_type='country')
    def city(country_id=None, city_id=None, **kwargs):

        if country_id is None and city_id is None:
            yield from city_ids.keys()

        if country_id is None and city_id is not None and city_id in city_ids:
            yield city_id

        if city_id is not None and country_id is not None and city_ids.get(city_id) == country_id:
            yield city_id

        if country_id is not None and city_id is None:
            yield from (k for k, v in city_ids.items() if v == country_id)

    return country_count, city_count, graph_model


@pytest.fixture()
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
      nodes {id ...ElementDetails}
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
