import itertools
from collections.abc import Iterable
from typing import Optional

import more_itertools
import networkx as nx
from matplotlib import pyplot


def sliding_window_visibility_graph(series: Iterable[float], window_size: Optional[int] = None):
    if window_size:
        yield from itertools.chain(
            visibility_graph(subseries) for subseries in more_itertools.sliding_window(series, window_size))
    else:
        yield visibility_graph(series)


def obstruction_predicate(n1, t1, n2, t2):
    slope = (t2 - t1) / (n2 - n1)
    constant = t2 - slope * n2

    def is_obstruction(n, t):
        return t >= constant + slope * n

    return is_obstruction


def visibility_graph(series: Iterable[float]):
    graph = nx.Graph()
    # Check all combinations of nodes n series

    for s1, s2 in itertools.combinations(enumerate(series), 2):
        n1, t1 = s1
        n2, t2 = s2

        if n2 == n1 + 1:
            graph.add_node(n1, value=t1)
            graph.add_node(n2, value=t2)
            graph.add_edge(n1, n2)
        else:
            is_obstruction = obstruction_predicate(n1, t1, n2, t2)
            obstructed = any(is_obstruction(n, t) for n, t in enumerate(series) if n1 < n < n2)
            if not obstructed:
                graph.add_edge(n1, n2)

    return graph


if __name__ == '__main__':
    series_list = [
        # range(10),
        # [2, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3, 4],
        [-(x ** 3) for x in range(-10, 11)],
        # [2, 1, 3, 4, 2, 1, 4, 3, 1, 1, 3, 4, 2, 4, 1, 3],
        # random.sample(range(1000), 500)
    ]

    for s in series_list:
        g = visibility_graph(s)
        print(g)

        pos = [[x, 0] for x in range(len(s))]
        labels = nx.get_node_attributes(g, 'value')
        nx.draw_networkx_nodes(g, pos)
        nx.draw_networkx_labels(g, pos, labels=labels)
        nx.draw_networkx_edges(g, pos, arrows=True, connectionstyle='arc3,rad=-1.57079632679')
        pyplot.show()
