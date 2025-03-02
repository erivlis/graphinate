import operator
from collections.abc import Iterable

import networkx as nx
import psutil

import graphinate


def processes_graph_model():
    """
    Create a graph model representing processes and their parent-child relationships.

    Returns:
        GraphModel: A graph model representing processes and their parent-child relationships.
    """

    graph_model = graphinate.model("Processes Graph")

    def processes() -> Iterable[psutil.Process]:
        for pid in psutil.pids():
            if psutil.pid_exists(pid):
                yield psutil.Process(pid)

    processes_list = [
        {
            'pid': p.pid,
            'name': p.name(),
            'parent_pid': p.parent().pid if p.parent() else None
        }
        for p in processes()
    ]

    @graph_model.node(key=operator.itemgetter('pid'), label=operator.itemgetter('name'))
    def process():
        yield from processes_list

    @graph_model.edge()
    def edge():
        for p in processes_list:
            parent_pid = p.get('parent_pid')
            if parent_pid:
                yield {'source': p.get('pid'), 'target': parent_pid}

    return graph_model


model = processes_graph_model()

if __name__ == '__main__':
    # 1. Define Graph Builder
    builder = graphinate.builders.NetworkxBuilder(model=model)

    # Then
    # 2. Build the Graph object
    graph: nx.Graph = builder.build()

    # Then
    # 3. Option A - Output to console
    print(graph)

    # Or
    # 3. Option B - Output as a plot
    graphinate.materializers.plot(graph)
