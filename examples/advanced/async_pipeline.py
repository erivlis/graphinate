# /// script
# dependencies = [
#   "graphinate",
# ]
# ///
import asyncio
import operator
from typing import Annotated

import graphinate
from graphinate import ParentId, abuild
from graphinate.builders import D3Builder, MermaidBuilder, NetworkxBuilder


def create_async_service_model() -> graphinate.GraphModel:
    """Create a model mixing async and synchronous node and edge suppliers."""
    service_model = graphinate.model(name='Hybrid Async/Sync Service Mesh')

    # 1. Async generator (async def + yield)
    @service_model.node(type_='cluster', key=operator.itemgetter('id'), label=operator.itemgetter('name'))
    async def clusters():
        await asyncio.sleep(0.01)
        yield {'id': 'prod', 'name': 'Production Cluster'}

    # 2. Async coroutine returning a collection (async def + return)
    @service_model.node(type_='service', parent_type='cluster', key=operator.itemgetter('id'))
    async def services(cluster_id: Annotated[str, ParentId('cluster')]):
        await asyncio.sleep(0.01)
        return [
            {'id': f'{cluster_id}-gateway'},
            {'id': f'{cluster_id}-auth'},
            {'id': f'{cluster_id}-billing'},
        ]

    # 3. Synchronous generator (def + yield) nested under an async parent
    @service_model.node(
        type_='endpoint',
        parent_type='service',
        key=operator.itemgetter('id'),
        unique=True,
    )
    def endpoints(service_id: Annotated[str, ParentId('service')]):
        if service_id.endswith('gateway'):
            yield {'id': f'{service_id}:/api/v1'}
        elif service_id.endswith('auth'):
            yield {'id': f'{service_id}:/oauth/token'}

    # 4. Async edge generator
    @service_model.edge(type_='calls', label=operator.itemgetter('protocol'))
    async def service_calls():
        await asyncio.sleep(0.01)
        yield {'source': 'prod-gateway', 'target': 'prod-auth', 'protocol': 'gRPC'}
        yield {'source': 'prod-gateway', 'target': 'prod-billing', 'protocol': 'HTTP/2'}

    # 5. Synchronous edge generator in the same model
    @service_model.edge(type_='routes_to')
    def endpoint_routes():
        yield {'source': 'prod-gateway:/api/v1', 'target': 'prod-auth:/oauth/token'}

    return service_model


async def main() -> None:
    model = create_async_service_model()

    nx_graph = await abuild(NetworkxBuilder, model)
    print('Hybrid Async/Sync NetworkX Graph:', nx_graph)

    d3_graph = await D3Builder(model).abuild()
    print(f"D3 Nodes: {len(d3_graph['nodes'])}, Links: {len(d3_graph['links'])}")

    mermaid_diagram = await MermaidBuilder(model).abuild()
    print('\nMermaid Diagram:\n' + mermaid_diagram)


if __name__ == '__main__':
    asyncio.run(main())
