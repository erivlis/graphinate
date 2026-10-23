# /// script
# dependencies = [
#   "graphinate",
# ]
# ///
import operator
from typing import Annotated

import graphinate
from graphinate import ParentId
from graphinate.builders import NetworkxBuilder
from graphinate.engine import EdgeEvent, GraphEngine, GraphObserver, NodeEvent


class AuditObserver(GraphObserver):
    """Custom observer that collects streaming statistics without building a graph."""

    def __init__(self) -> None:
        self.model_name: str = ''
        self.nodes_by_type: dict[str, int] = {}
        self.edge_count: int = 0

    def on_start(self, model_name: str) -> None:
        self.model_name = model_name
        self.nodes_by_type.clear()
        self.edge_count = 0

    def on_node(self, event: NodeEvent) -> None:
        self.nodes_by_type[event.type] = self.nodes_by_type.get(event.type, 0) + 1

    def on_edge(self, event: EdgeEvent) -> None:
        self.edge_count += 1

    def on_finish(self) -> None:
        print(f'Audit complete ({self.model_name}): {self.nodes_by_type}, total edges={self.edge_count}')


def create_cloud_topology_model() -> graphinate.GraphModel:
    cloud_model = graphinate.model(name='Cloud Topology')

    @cloud_model.node(type_='region', key=operator.itemgetter('id'), label=operator.itemgetter('name'))
    def regions():
        yield {'id': 'us-east', 'name': 'US East'}
        yield {'id': 'eu-west', 'name': 'EU West'}

    @cloud_model.node(type_='vpc', parent_type='region', key=operator.itemgetter('id'))
    def vpcs(region_id: Annotated[str, ParentId('region')]):
        yield {'id': f'{region_id}-vpc-1'}

    @cloud_model.node(
        type_='service',
        parent_type='vpc',
        key=operator.itemgetter('id'),
        unique=True,
    )
    def services(
        region_id: Annotated[str, ParentId('region')],
        vpc_id: Annotated[str, ParentId('vpc')],
    ):
        yield {'id': f'{vpc_id}-api', 'region': region_id}
        yield {'id': f'{vpc_id}-db', 'region': region_id}

    @cloud_model.edge(type_='peering')
    def peering_links():
        yield {'source': 'us-east-vpc-1-api', 'target': 'eu-west-vpc-1-api'}

    return cloud_model


if __name__ == '__main__':
    topology_model = create_cloud_topology_model()
    audit_observer = AuditObserver()
    nx_builder = NetworkxBuilder(topology_model)

    # Execute a single traversal pass that notifies both observers simultaneously
    engine = GraphEngine(topology_model)
    engine.subscribe(audit_observer)
    engine.subscribe(nx_builder)
    engine.run()
    print('NetworkX Graph summary:', nx_builder._graph)
