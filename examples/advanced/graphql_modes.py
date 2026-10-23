# /// script
# dependencies = [
#   "graphinate",
# ]
# ///
import graphinate
from graphinate import CompositionStrategy, SchemaMode
from graphinate.builders import GraphQLBuilder, NetworkxBuilder


def create_composed_model() -> graphinate.GraphModel:
    compute_model = graphinate.model(name='Compute')

    @compute_model.node(type_='service')
    def compute_services():
        yield 'api-gateway'
        yield 'worker'

    storage_model = graphinate.model(name='Storage')

    @storage_model.node(type_='database')
    def databases():
        yield 'postgres-primary'

    @storage_model.edge(type_='reads_from')
    def connections():
        yield {'source': 'api-gateway', 'target': 'postgres-primary'}
        yield {'source': 'worker', 'target': 'postgres-primary'}

    return compute_model.merge(
        storage_model,
        strategy=CompositionStrategy.MERGE,
        name='Platform Graph',
    )


if __name__ == '__main__':
    platform_model = create_composed_model()

    # 1. Dynamic Schema Mode (generates ServiceNode, DatabaseNode, services, databases)
    dynamic_schema = GraphQLBuilder(platform_model, mode=SchemaMode.DYNAMIC).build()
    dynamic_result = dynamic_schema.execute_sync(
        '{ services { label neighbors { type label } } databases { label } }'
    )
    print('Dynamic Schema Result:', dynamic_result.data)

    # 2. Static Schema Mode (uses a single GenericGraphNode and fixed root fields)
    static_schema = GraphQLBuilder(platform_model, mode=SchemaMode.STATIC).build()
    static_result = static_schema.execute_sync(
        '{ nodes { type label } edges { type label } }'
    )
    print('Static Schema Result:', static_result.data)

    # 3. Context-Injected Graph Execution (override the backing NetworkX graph per request)
    custom_graph = NetworkxBuilder(platform_model).build()
    custom_graph.graph['name'] = 'Context-Injected Snapshot'
    injected_result = static_schema.execute_sync(
        '{ graph { name nodeCount edgeCount } }',
        context_value={'graph': custom_graph},
    )
    print('Context-Injected Result:', injected_result.data)
