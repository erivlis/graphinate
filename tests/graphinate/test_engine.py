"""Unit tests for GraphEngine, GraphObserver, NodeEvent, and EdgeEvent."""

import operator
from typing import Annotated

from graphinate import (
    EdgeEvent,
    GraphEngine,
    GraphObserver,
    Multiplicity,
    NodeEvent,
    ParentId,
    model,
)
from graphinate.typing import UniverseNode


class RecordingObserver:
    """Test observer that records all engine lifecycle events."""

    def __init__(self):
        self.started_with: str | None = None
        self.finished: bool = False
        self.nodes: list[NodeEvent] = []
        self.edges: list[EdgeEvent] = []

    def on_start(self, name: str) -> None:
        self.started_with = name

    def on_node(self, event: NodeEvent) -> None:
        self.nodes.append(event)

    def on_edge(self, event: EdgeEvent) -> None:
        self.edges.append(event)

    def on_finish(self) -> None:
        self.finished = True


def test_recording_observer_satisfies_protocol():
    obs = RecordingObserver()
    assert isinstance(obs, GraphObserver)


def test_graph_engine_emits_lifecycle_events():
    m = model(name='Engine Test Model')

    @m.node(type_='org', key=operator.itemgetter('id'), label=operator.itemgetter('name'))
    def orgs():
        yield {'id': 'o1', 'name': 'Org 1'}

    @m.node(
        type_='repo',
        parent_type='org',
        key=operator.itemgetter('id'),
        label='StaticRepoLabel',
        multiplicity=Multiplicity.LAST,
    )
    def repos(oid: Annotated[str, ParentId('org')]):
        if oid == 'o1':
            yield {'id': 'r1', 'name': 'Repo 1'}

    @m.edge(type_='stars', label=lambda item: f"{item['source']}->{item['target']}", weight=2.5)
    def stars():
        yield {'source': 'o1', 'target': 'r1'}

    obs1 = RecordingObserver()
    obs2 = RecordingObserver()

    engine = GraphEngine(m)
    engine.subscribe(obs1)
    engine.subscribe(obs2)
    engine.run()

    for obs in (obs1, obs2):
        assert obs.started_with == 'Engine Test Model'
        assert obs.finished is True
        assert len(obs.nodes) == 2

        org_event, repo_event = obs.nodes
        assert org_event.node_id == ('o1',)
        assert org_event.type == 'org'
        assert org_event.label == 'Org 1'
        assert org_event.lineage == ('o1',)
        assert org_event.multiplicity == Multiplicity.ALL

        assert repo_event.node_id == ('r1',)
        assert repo_event.type == 'repo'
        assert repo_event.label == 'StaticRepoLabel'
        assert repo_event.lineage == ('o1', 'r1')
        assert repo_event.multiplicity == Multiplicity.LAST

        assert len(obs.edges) == 2
        hierarchy_edge, explicit_edge = obs.edges
        assert hierarchy_edge.is_hierarchy is True
        assert hierarchy_edge.source_id == ('o1',)
        assert hierarchy_edge.target_id == ('r1',)

        assert explicit_edge.is_hierarchy is False
        assert explicit_edge.source_id == ('o1',)
        assert explicit_edge.target_id == ('r1',)
        assert explicit_edge.type == 'stars'
        assert explicit_edge.label == 'o1->r1'
        assert explicit_edge.weight == 2.5


def test_graph_engine_parent_node_id_resolution():
    assert GraphEngine._parent_node_id((UniverseNode, 'child')) is UniverseNode
    res = GraphEngine._parent_node_id(('org', 'repo'), org_id='o1', repo_id='r1')
    assert res == ('o1',)
