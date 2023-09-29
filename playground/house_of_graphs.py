from collections.abc import Iterable, Mapping
from pprint import pprint
from typing import Union

import networkx as nx


def parse(adjacency_list: str) -> Iterable[tuple[int, list[int]]]:
    for line in adjacency_list.strip().splitlines():
        s, tl = line.split(":")
        yield int(s), [int(t) for t in tl.strip().split()]


def adjacency_mapping(adjacency_list: str) -> Mapping[int, list[int]]:
    return dict(parse(adjacency_list))


def edges_iter(adjacency_source: Union[str, Mapping[int, list[int]]]) -> Iterable[tuple[int, int]]:
    if isinstance(adjacency_source, str):
        adjacency_list = parse(adjacency_source)
    elif isinstance(adjacency_source, Mapping):
        adjacency_list = adjacency_source.items()
    else:
        raise TypeError("'adjacency_source' should be a 'str' or a Mapping[int, list[int]]")

    for s, tl in adjacency_list:
        for t in tl:
            yield int(s), int(t)


def graph(adjacency_source: Union[str, Mapping[int, list[int]]]) -> nx.Graph():
    return nx.Graph(list(edges_iter(adjacency_source)))


if __name__ == '__main__':
    a = """
1: 4 15
2: 8 17
3: 8 17
4: 1 14
5: 7 14
6: 7 14
7: 5 6
8: 2 3
9: 11 16
10: 13 15
11: 9 12
12: 11 16 17
13: 10 16 17
14: 4 5 6 15
15: 1 10 14 16
16: 9 12 13 15
17: 2 3 12 13
    """

    m = adjacency_mapping(a)

    pprint(m)
